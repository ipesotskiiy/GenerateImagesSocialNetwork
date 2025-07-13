from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from message.models import ChatMessage
from message.schemas import MessageRead, MessageCreate, MessageUpdate
from settings import get_session

router = APIRouter(
    prefix="/message",
    tags=["message 💬"]

)

@router.post("/create/", response_model=MessageRead, summary="Создать сообщение", status_code=201)
async def create_message(message: MessageCreate, session: AsyncSession = Depends(get_session)):
    db_message = ChatMessage(**message.dict())
    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message

@router.patch("/update/{message_id}", response_model=MessageRead, summary="Изменить сообщение")
async def update_message(message_id: int, message: MessageUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ChatMessage).where(ChatMessage.id==message_id))
    db_message = result.scalar_one_or_none()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.content is not None:
        db_message.content = message.content
    await session.commit()
    await session.refresh(db_message)
    return db_message

@router.delete("/delete/{message_id}", status_code=204)
async def delete_message(message_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ChatMessage).where(ChatMessage.id==message_id))
    db_message = result.scalar_one_or_none()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    await session.delete(db_message)
    await session.commit()
    return "Сообщение удалено"

@router.get("/get/{message_id}", response_model=MessageRead)
async def get_message(message_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    db_message = result.scalar_one_or_none()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return

@router.get("/dialog/{user1_id}/{user2_id}/", response_model=list[MessageRead])
async def get_dialog_messages(user1_id: int, user2_id: int, session: AsyncSession = Depends(get_session)):
    query = select(ChatMessage).where(
        or_(
            (ChatMessage.sender_id == user1_id) & (ChatMessage.recipient_id == user2_id),
            (ChatMessage.sender_id == user2_id) & (ChatMessage.recipient_id == user1_id)
        )
    ).order_by(ChatMessage.timestamp.asc())

    result = await session.execute(query)
    messages = result.scalars().all()
    return messages


