from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Meeting, MeetingParticipant, User
from app.auth import get_current_active_user

router = APIRouter()

class MeetingParticipantResponse(BaseModel):
    id: int
    name: str
    email: str
    response: str

class MeetingResponse(BaseModel):
    id: int
    chat_id: int
    title: str
    start_utc: datetime
    end_utc: datetime
    description: str
    status: str
    participants: List[MeetingParticipantResponse]
    
    class Config:
        from_attributes = True

class ConfirmRequest(BaseModel):
    user_id: int

@router.get("/meetings", response_model=List[MeetingResponse])
async def get_meetings_by_chat(
    chat_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    meetings = db.query(Meeting).filter(Meeting.chat_id == chat_id).all()
    
    meeting_responses = []
    for meeting in meetings:
        # Get participants with user details
        participants = db.query(MeetingParticipant, User) \
            .join(User, MeetingParticipant.user_id == User.id) \
            .filter(MeetingParticipant.meeting_id == meeting.id) \
            .all()
        
        participant_responses = []
        for participant, user in participants:
            participant_responses.append(MeetingParticipantResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                response=participant.response
            ))
        
        meeting_responses.append(MeetingResponse(
            id=meeting.id,
            chat_id=meeting.chat_id,
            title=meeting.title,
            start_utc=meeting.start_utc,
            end_utc=meeting.end_utc,
            description=meeting.description,
            status=meeting.status,
            participants=participant_responses
        ))
    
    return meeting_responses

@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    #getting participants with user details.
    participants = db.query(MeetingParticipant, User) \
        .join(User, MeetingParticipant.user_id == User.id) \
        .filter(MeetingParticipant.meeting_id == meeting_id) \
        .all()
    
    participant_responses = []
    for participant, user in participants:
        participant_responses.append(MeetingParticipantResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            response=participant.response
        ))
    
    # Create response object instead of modifying SQLAlchemy object
    return MeetingResponse(
        id=meeting.id,
        chat_id=meeting.chat_id,
        title=meeting.title,
        start_utc=meeting.start_utc,
        end_utc=meeting.end_utc,
        description=meeting.description,
        status=meeting.status,
        participants=participant_responses
    )

@router.post("/meetings/{meeting_id}/confirm")
async def confirm_meeting(meeting_id: int, request: ConfirmRequest, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    participant = db.query(MeetingParticipant) \
        .filter(MeetingParticipant.meeting_id == meeting_id) \
        .filter(MeetingParticipant.user_id == request.user_id) \
        .first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    participant.response = "confirmed"
    db.commit()
    
    return {"status": "confirmed", "message": "Meeting confirmed successfully"}
