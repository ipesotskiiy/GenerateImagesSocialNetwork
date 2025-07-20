from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from message.models import ChatMessage
from message.schemas import MessageCreate, MessageUpdate
from settings import get_session


async def create_message(session: AsyncSession, sender_id: int, recipient_id: int, content: str) -> ChatMessage:
    db_message = ChatMessage(sender_id=sender_id, recipient_id=recipient_id, content=content)
    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message


async def update_message(session: AsyncSession, message_id: int, new_content: str) -> ChatMessage:
    result = await session.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    db_message = result.scalar_one_or_none()
    if db_message:
        db_message.content = new_content
        await session.commit()
        await session.refresh(db_message)
    return db_message

async def delete_message(session: AsyncSession, message_id: int) -> bool:
    result = await session.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    db_message = result.scalar_one_or_none()
    if db_message:
        await session.delete(db_message)
        await session.commit()
        return True
    return False

async def get_message(message_id: int, session: AsyncSession = Depends(get_session)) -> ChatMessage:
    result = await session.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    db_message = result.scalar_one_or_none()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message