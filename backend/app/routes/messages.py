from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Message, User, Chat
from app.auth import get_current_active_user

router = APIRouter()

class MessageCreate(BaseModel):
    chat_id: int
    user_id: int
    text: str

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    text: str
    created_at: datetime
    user_name: str
    
    class Config:
        from_attributes = True

@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message: MessageCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    #verify user exists or not 
    user = db.query(User).filter(User.id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    #verify chat exists or not
    chat = db.query(Chat).filter(Chat.id == message.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    #create message
    db_message = Message(
        chat_id=message.chat_id,
        user_id=message.user_id,
        text=message.text
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    #add user name to response
    response = MessageResponse(
        id=db_message.id,
        chat_id=db_message.chat_id,
        user_id=db_message.user_id,
        text=db_message.text,
        created_at=db_message.created_at,
        user_name=user.name
    )
    
    return response

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    #verify chat exists or not?
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    #get messages with user informations--
    messages = db.query(Message, User.name.label('user_name')) \
        .join(User, Message.user_id == User.id) \
        .filter(Message.chat_id == chat_id) \
        .order_by(Message.created_at.asc()) \
        .all()
    
    response = []
    for message, user_name in messages:
        response.append(MessageResponse(
            id=message.id,
            chat_id=message.chat_id,
            user_id=message.user_id,
            text=message.text,
            created_at=message.created_at,
            user_name=user_name
        ))
    
    return response

@router.get("/chats/{chat_id}/participants")
async def get_chat_participants(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify chat exists
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Get unique participants from messages in this chat
    participants = db.query(User.id, User.name, User.email) \
        .join(Message, User.id == Message.user_id) \
        .filter(Message.chat_id == chat_id) \
        .distinct() \
        .all()
    
    return [{"id": p.id, "name": p.name, "email": p.email} for p in participants]
