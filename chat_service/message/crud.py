from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from message.models import ChatMessage
from publisher import publish_new, publish_edit, publish_delete

async def create_message(session: AsyncSession, sender_id: int, recipient_id: int, content: str) -> ChatMessage:
    db_message = ChatMessage(sender_id=sender_id, recipient_id=recipient_id, content=content)
    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)

    await publish_new({
        "type": "new",
        "id": db_message.id,
        "sender_id": db_message.sender_id,
        "recipient_id": db_message.recipient_id,
        "content": db_message.content,
        "timestamp": db_message.timestamp.isoformat(),
    })
    return db_message

async def update_message(session: AsyncSession, message_id: int, new_content: str) -> ChatMessage | None:
    res = await session.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    db_message = res.scalar_one_or_none()
    if not db_message:
        return None

    db_message.content = new_content
    await session.commit()
    await session.refresh(db_message)

    await publish_edit({
        "type": "edit",
        "message_id": db_message.id,
        "sender_id": db_message.sender_id,
        "recipient_id": db_message.recipient_id,
        "new_content": db_message.content,
    })
    return db_message

async def delete_message(session: AsyncSession, message_id: int) -> bool:
    res = await session.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    db_message = res.scalar_one_or_none()
    if not db_message:
        return False

    sender_id, recipient_id = db_message.sender_id, db_message.recipient_id
    await session.delete(db_message)
    await session.commit()

    await publish_delete({
        "type": "delete",
        "message_id": message_id,
        "sender_id": sender_id,
        "recipient_id": recipient_id,
    })
    return True

async def get_message(message_id: int, session: AsyncSession) -> ChatMessage | None:
    res = await session.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    return res.scalar_one_or_none()