from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import AsyncSessionLocal
from app.models import Thread, Message

router = APIRouter()
BASE_URL = "/api/v1/threads"


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.post(path=BASE_URL, status_code=status.HTTP_201_CREATED)
async def create_thread(session: AsyncSession = Depends(get_session)):
    new_thread = Thread(id=str(uuid.uuid4()))
    session.add(new_thread)
    await session.commit()
    return {"id": new_thread.id, "created_at": new_thread.created_at}



@router.post(path=BASE_URL + "/{thread_id}/messages", status_code=status.HTTP_201_CREATED)
async def create_message(thread_id: str, session: AsyncSession = Depends(get_session)):
    thread = await session.get(Thread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    new_message = Message(id=str(uuid.uuid4()), thread_id=thread_id)
    session.add(new_message)
    await session.commit()
    return {"id": new_message.id, "answer": new_message.answer, "created_at": new_message.created_at}
