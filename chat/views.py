import json
import logging
import uuid
from typing import List

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import views, status
from rest_framework.request import Request
from rest_framework.response import Response

from chat.models import MessageV2, Thread, Message
from chat.serializers import (
    ChatInputV2Serializer,
    MessageSerializerV2,
    ThreadShortSerializer,
    ChatInputSerializer,
    MessageSerializer
)
from graph import LangGraphLLM
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


def get_sorted_messages(thread: Thread) -> List[Message]:
    messages = Message.objects.filter(thread=thread).order_by("created_at")
    return list(messages)


def get_input_str(request: Request) -> str:
    serializer = ChatInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data.get("input")

# class MessageCreateAPIView(views.APIView):
#
#     @swagger_auto_schema(
#         request_body=ChatInputSerializer,
#         responses={status.HTTP_201_CREATED: MessageSerializer()}
#     )
#     def post(self, request: Request, **kwargs) -> Response:
#         logger.info(f"Processing new message for thread (uuid): {self.kwargs.get('uuid')}")
#         thread = self.get_thread_from_req()
#         messages = get_sorted_messages(thread)
#
#         input_query = get_input_str(request)
#         logger.info(f'Input query: {input_query}, thread: {thread.uuid}')
#
#         llm = OpenAILangChain()
#         for message in messages:
#             llm.add_history(user=message.input, ai=message.answer)
#
#         response = llm.predict(input_query)
#         logger.info(f'Response: {json.dumps(response, indent=4, ensure_ascii=False)}')
#         message = Message.objects.create(
#             thread=thread,
#             input=response['english_input'],
#             answer=response['assistant_help'],
#             answer_in_lang=response['final_response'],
#             original_input=input_query,
#             lang=response['language'],
#         )
#         return Response(MessageSerializer(instance=message).data, status=status.HTTP_201_CREATED)
#
#     def get_thread_from_req(self) -> Thread:
#         thread_uuid = self.kwargs.get('uuid')
#         thread = get_object_or_404(Thread, uuid=thread_uuid)
#         return thread


class MessageCreateAPIView(views.APIView):

    @swagger_auto_schema(
        request_body=ChatInputSerializer,
        responses={status.HTTP_201_CREATED: MessageSerializer()}
    )
    def post(self, request: Request, **kwargs) -> Response:
        logger.info(f"Processing new message for thread (uuid): {self.kwargs.get('uuid')}")
        thread = self.get_thread_from_req()
        messages = get_sorted_messages(thread)

        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_query = serializer.validated_data.get("input")
        context = serializer.validated_data.get("context")

        logger.info(f'Input query: {input_query}, thread: {thread.uuid}')
        logger.info(f'Context: {context}')

        llm = OpenAILangChain()
        for message in messages:
            llm.add_history(user=message.input, ai=message.answer)

        response = llm.predict(input_query)
        logger.info(f'Response: {json.dumps(response, indent=4, ensure_ascii=False)}')
        message = Message.objects.create(
            thread=thread,
            input=response['english_input'],
            answer=response['assistant_help'],
            answer_in_lang=response['final_response'],
            original_input=input_query,
            lang=response['language'],
        )
        return Response(MessageSerializer(instance=message).data, status=status.HTTP_201_CREATED)

    def get_thread_from_req(self) -> Thread:
        thread_uuid = self.kwargs.get('uuid')
        thread = get_object_or_404(Thread, uuid=thread_uuid)
        return thread


class MessageCreateV2APIView(views.APIView):

    @swagger_auto_schema(
        request_body=ChatInputV2Serializer,
        responses={status.HTTP_201_CREATED: MessageSerializer()},
    )
    def post(self, request: Request, **kwargs) -> Response:
        logger.info(
            f"Processing new message for thread (uuid): {self.kwargs.get('uuid')}"
        )
        thread = self.get_thread_from_req()

        serializer = ChatInputV2Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_query = serializer.validated_data.get("input")

        logger.info(f"Input query: {input_query}, thread: {thread.uuid}")

        llm = LangGraphLLM()
        response = llm.predict(input_query=input_query, question_type=serializer.validated_data.get("question_type"))
        logger.info(f"Response: {json.dumps(response, indent=4, ensure_ascii=False)}")
        messagev2 = MessageV2.objects.create(
            thread=thread,
            input=response["question"],
            answer=response["response"],
        )
        return Response(MessageSerializerV2(instance=messagev2).data, status=status.HTTP_201_CREATED)

    def get_thread_from_req(self) -> Thread:
        thread_uuid = self.kwargs.get("uuid")
        thread = get_object_or_404(Thread, uuid=thread_uuid)
        return thread