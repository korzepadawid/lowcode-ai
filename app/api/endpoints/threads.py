import logging
import uuid
import os
import httpx

from openai import OpenAI
from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.dto import Input
from app.models import Thread, Message

BASE_URL = "/api/v1/threads"

router = APIRouter()

log = logging.getLogger("uvicorn.error")
client = OpenAI(
    api_key=os.getenv("OPEN_AI_API_KEY"), project=os.getenv("OPEN_AI_PROJECT_ID")
)
timeout = httpx.Timeout(timeout=10.0, connect=5.0)


@router.post(path=BASE_URL, status_code=status.HTTP_201_CREATED)
async def create_thread(session: AsyncSession = Depends(get_session)):
    """
    Creates a new thread using the OpenAI API and saves it to the database.

    This function creates an empty thread through the OpenAI API, logs the
    thread ID, generates a new UUID for the thread, and stores the thread
    information in the database.
    """
    new_thread = Thread(id=str(uuid.uuid4()))
    session.add(new_thread)
    await session.commit()
    return {"id": new_thread.id, "created_at": new_thread.created_at}


@router.post(
    path=BASE_URL + "/{thread_id}/messages", status_code=status.HTTP_201_CREATED
)
async def create_message(
    input: Input, thread_id: str, session: AsyncSession = Depends(get_session)
):
    """
    Creates a new message in an existing thread and saves it to the database.

    This function retrieves a thread by its ID, checks if the thread exists,
    gathers all existing messages in the thread, constructs the context for
    the chat completion using the OpenAI API, generates a response, and
    stores the new message in the database.
    """
    thread = await session.get(Thread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    result = await session.execute(
        select(Message)
        .where(Message.thread_id == thread_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    ctx_messages = [
        {
            "role": "system",
            "content": "You are an assistant for a lowcode platform, you're going to help with JavaScript and C#",
        },
    ]
    for message in messages:
        ctx_messages.append({"role": "user", "content": message.input})
        ctx_messages.append({"role": "system", "content": message.answer})

    ctx_messages.append({"role": "user", "content": input.input})

    chat_completion = client.chat.completions.create(
        messages=ctx_messages,
        model="gpt-4",
    )

    response = chat_completion.choices[0].message.content
    new_message = Message(
        id=str(uuid.uuid4()), thread_id=thread_id, input=input.input, answer=response
    )
    session.add(new_message)
    await session.commit()
    return {
        "id": new_message.id,
        "answer": new_message.answer,
        "created_at": new_message.created_at,
    }
