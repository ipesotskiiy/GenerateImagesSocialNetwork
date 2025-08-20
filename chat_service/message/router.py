from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from message.crud import create_message, update_message, delete_message, get_message
from message.models import ChatMessage
from message.schemas import MessageRead, MessageCreate, MessageUpdate
from settings import get_session

router = APIRouter(
    prefix="/message",
    tags=["message 💬"]

)

@router.post("/create/", response_model=MessageRead)
async def create_message_http(
    message: MessageCreate, session: AsyncSession = Depends(get_session)
):
    return await create_message(session, message.sender_id, message.recipient_id, message.content)

@router.patch("/update/{message_id}", response_model=MessageRead)
async def update_message_http(
    message_id: int, message: MessageUpdate, session: AsyncSession = Depends(get_session)
):
    updated = await update_message(session, message_id, message.content)
    if updated is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return updated

@router.delete("/delete/{message_id}", status_code=204)
async def delete_message_http(
    message_id: int, session: AsyncSession = Depends(get_session)
):
    success = await delete_message(session, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")

@router.get("/get/{message_id}", response_model=MessageRead)
async def get_message_api(message_id: int, session: AsyncSession = Depends(get_session)):
    return  await get_message(message_id, session)

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


