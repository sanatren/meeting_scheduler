from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.scheduling_agent import SchedulingAgent

router = APIRouter()

class ScheduleRequest(BaseModel):
    chat_id: int

class ScheduleResponse(BaseModel):
    status: str
    meeting: Optional[dict] = None
    ask: Optional[str] = None
    message: Optional[str] = None

@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_meeting(request: ScheduleRequest, db: Session = Depends(get_db)):
    agent = SchedulingAgent(db)
    
    try:
        result = await agent.process_chat_for_scheduling(request.chat_id)
        return ScheduleResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
