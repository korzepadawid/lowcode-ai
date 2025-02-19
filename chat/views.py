import json
import logging
import time
import uuid
from typing import List

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import views, status
from rest_framework.request import Request
from rest_framework.response import Response

from chat.models import Message, Thread, Message
from chat.serializers import (
    ChatInputSerializer,
    MessageSerializer,
    ThreadShortSerializer,
    ChatInputSerializer,
    MessageSerializer,
)
from llm.graph import GENERAL, LangGraphLLM
from langchainopenai import OpenAILangChain

logger = logging.getLogger("chat")


class ThreadCreateAPIView(views.APIView):
    serializer_class = ThreadShortSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Thread created successfully",
                schema=ThreadShortSerializer(),
            ),
        }
    )
    def post(self, _: Request) -> Response:
        generated_uuid = uuid.uuid4()
        serializer = self.serializer_class(
            data={
                "uuid": generated_uuid,
            }
        )
        if serializer.is_valid():
            thread = Thread.objects.create(uuid=generated_uuid)
            response_serializer = self.serializer_class(thread)
            logger.info(f"Thread created: {generated_uuid}")
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_sorted_messages_v2(thread: Thread) -> List[Message]:
    messages = Message.objects.filter(thread=thread).order_by("created_at")
    return list(messages)


def get_input_str(request: Request) -> str:
    serializer = ChatInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data.get("input")


class MessageCreateAPIView(views.APIView):

    @swagger_auto_schema(
        request_body=ChatInputSerializer,
        responses={status.HTTP_201_CREATED: MessageSerializer()},
    )
    def post(self, request: Request, **kwargs) -> Response:
        logger.info(
            f"Processing new message for thread (uuid): {self.kwargs.get('uuid')}"
        )
        thread = self.get_thread_from_req()

        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_query = serializer.validated_data.get("input")

        logger.info(f"Input query: {input_query}, thread: {thread.uuid}")
        logger.info(f"Context: {serializer.validated_data.get('context', {})}")
        context = serializer.validated_data.get("context", {})

        try:
            llm = LangGraphLLM(thread_id=thread.uuid, context=context)
            messages = get_sorted_messages_v2(thread)

            for message in messages:
                llm.add_history(user=message.input_translated, ai=message.answer_translated)
                llm.add_base_history(user=message.input, ai=message.answer)

            response = llm.predict(
                input_query=input_query,
                question_type=GENERAL,
            )
            message = Message.objects.create(
                thread=thread,
                input=response["question"],
                answer=response["response"],
                input_translated=response["question_in_english"],
                answer_translated=response["response_in_english"],
            )
            return Response(
                MessageSerializer(instance=message).data, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            message_instance = Message(
                id=-1,
                answer="Wybacz, ale nie mogłem udzielić odpowiedzi, stwórz nowy wątek i zadaj pytanie ponownie 🤗",
                created_at=now(),
            )
            serializer = MessageSerializer(message_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_thread_from_req(self) -> Thread:
        thread_uuid = self.kwargs.get("uuid")
        thread = get_object_or_404(Thread, uuid=thread_uuid)
        return thread
