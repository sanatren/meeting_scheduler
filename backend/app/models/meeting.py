from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    title = Column(String, nullable=True)
    start_utc = Column(DateTime(timezone=True), nullable=False)
    end_utc = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, confirmed, cancelled   #maker tool for decision
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat = relationship("Chat", back_populates="meetings")
    participants = relationship("MeetingParticipant", back_populates="meeting")

class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False)
    response = Column(String, default="invited")  # invited, confirmed, declined
    
    # Relationships
    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="meeting_participants")
