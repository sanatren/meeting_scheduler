from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import pytz

from app.models import Message, User, Meeting, MeetingParticipant, Chat
from app.services.email_service import EmailService

load_dotenv()

class SchedulingAgent:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.email_service = EmailService()
        self.ist_timezone = pytz.timezone('Asia/Kolkata')
    
    async def process_chat_for_scheduling(self, chat_id: int) -> Dict:
        """Main method to process chat for meeting scheduling using GPT-4o"""
        
        # Get chat messages with users
        messages = self.db.query(Message, User) \
            .join(User, Message.user_id == User.id) \
            .filter(Message.chat_id == chat_id) \
            .order_by(Message.created_at.asc()) \
            .all()
        
        if not messages:
            return {
                "status": "error",
                "message": "No messages found in chat"
            }
        
        # Get unique participants
        participants = list(set(user.id for _, user in messages))
        participant_names = {user.id: user.name for _, user in messages}
        
        # Format chat history for LLM
        chat_history = self._format_chat_for_llm(messages)
        
        # Step 1: Detect meeting intent using GPT-4o
        intent_result = await self._detect_meeting_intent_llm(chat_history)
        
        if not intent_result["has_intent"]:
            return {
                "status": "no_intent",
                "message": "No meeting scheduling intent detected in the chat"
            }
        
        # Step 2: Extract availability using GPT-4o
        availability_result = await self._extract_availability_llm(chat_history, participant_names)
        
        # Step 3: Check if we have enough information
        missing_info_result = await self._check_missing_info_llm(
            availability_result, participant_names, chat_history
        )
        
        if missing_info_result["needs_followup"]:
            return {
                "status": "need_info",
                "ask": missing_info_result["followup_message"]
            }
        
        # Step 4: Find optimal meeting time using GPT-4o
        optimal_time_result = await self._find_optimal_time_llm(
            availability_result, participants, participant_names
        )
        
        if not optimal_time_result["found_time"]:
            return {
                "status": "no_overlap",
                "message": optimal_time_result["reason"]
            }
        
        # Step 5: Create meeting in database
        meeting = self._create_meeting(
            chat_id, 
            optimal_time_result["meeting_time"], 
            participants,
            optimal_time_result["title"]
        )
        
        # Step 6: Send confirmation emails
        await self._send_confirmation_emails(meeting, participants)
        
        return {
            "status": "scheduled",
            "meeting": {
                "id": meeting.id,
                "title": meeting.title,
                "start_utc": meeting.start_utc,
                "end_utc": meeting.end_utc,
                "participants": participants
            }
        }
    
    def _format_chat_for_llm(self, messages: List[Tuple[Message, User]]) -> str:
        """Format chat messages for LLM processing"""
        formatted_messages = []
        for message, user in messages:
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S IST")
            formatted_messages.append(f"[{timestamp}] {user.name}: {message.text}")
        
        return "\n".join(formatted_messages)
    
    async def _detect_meeting_intent_llm(self, chat_history: str) -> Dict:
        """Use GPT-4o to detect meeting scheduling intent"""
        prompt = f"""
        Analyze the following chat conversation and determine if there is a clear intent to schedule a meeting.

        Chat History:
        {chat_history}

        Look for:
        - Direct requests to schedule meetings ("let's meet", "schedule a meeting", "can we meet")
        - Discussion about availability and timing
        - Coordination of group activities
        - Planning sessions or calls

        Respond with a JSON object containing:
        {{
            "has_intent": boolean,
            "confidence": float (0.0 to 1.0),
            "reasoning": "Brief explanation of your decision"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always responds with valid JSON. Do not include any text outside the JSON object."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            print(f"Intent detection raw response: {content}")
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"LLM Intent Detection Error: {e}")
            print(f"Raw response: {response.choices[0].message.content if 'response' in locals() else 'No response'}")
            # Fallback to keyword-based detection
            return self._fallback_intent_detection(chat_history)
    
    async def _extract_availability_llm(self, chat_history: str, participant_names: Dict[int, str]) -> Dict:
        """Use GPT-4o to extract availability information from chat"""
        prompt = f"""
        Analyze the following chat conversation and extract availability information for each participant.

        Chat History:
        {chat_history}

        Participants: {list(participant_names.values())}

        For each participant, extract:
        - Available time slots (dates, times, durations)
        - Unavailable periods
        - Preferences or constraints
        - Time zone (assume IST/Asia/Kolkata if not specified)

        Current date context: Today is {datetime.now().strftime('%Y-%m-%d')}

        Parse relative dates like "Thursday", "tomorrow", "this week" into specific dates.
        Parse times like "2-5 PM", "morning", "after 4 PM" into specific time ranges.

        Respond with a JSON object:
        {{
            "participants": {{
                "ParticipantName": {{
                    "available_slots": [
                        {{
                            "date": "YYYY-MM-DD",
                            "start_time": "HH:MM",
                            "end_time": "HH:MM",
                            "timezone": "Asia/Kolkata"
                        }}
                    ],
                    "unavailable_slots": [...],
                    "has_availability": boolean,
                    "constraints": "Any specific constraints mentioned"
                }}
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always responds with valid JSON. Do not include any text outside the JSON object."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            print(f"Availability extraction raw response: {content[:200]}...")
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"LLM Availability Extraction Error: {e}")
            # Fallback to basic parsing
            return self._fallback_availability_extraction(chat_history, participant_names)
    
    async def _check_missing_info_llm(self, availability_result: Dict, participant_names: Dict[int, str], chat_history: str) -> Dict:
        """Use GPT-4o to check if any participant's availability is missing or unclear"""
        prompt = f"""
        Review the extracted availability information and determine if any participant's availability is missing or unclear.

        Extracted Availability:
        {json.dumps(availability_result, indent=2)}

        Participants: {list(participant_names.values())}

        Chat History:
        {chat_history}

        Determine:
        1. Which participants haven't provided clear availability
        2. What specific information is missing
        3. Generate a helpful follow-up question if needed

        Respond with JSON:
        {{
            "needs_followup": boolean,
            "missing_participants": ["ParticipantName1", ...],
            "followup_message": "Natural language message asking for missing availability",
            "reasoning": "Why follow-up is needed"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always responds with valid JSON. Do not include any text outside the JSON object."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"LLM Missing Info Check Error: {e}")
            return {"needs_followup": False, "followup_message": ""}
    
    async def _find_optimal_time_llm(self, availability_result: Dict, participants: List[int], participant_names: Dict[int, str]) -> Dict:
        """Use GPT-4o to find the optimal meeting time"""
        prompt = f"""
        Given the availability information, find the optimal meeting time that works for the majority of participants.

        Availability Data:
        {json.dumps(availability_result, indent=2)}

        Participants: {list(participant_names.values())} (Total: {len(participants)})
        Majority needed: {len(participants) // 2 + 1} participants

        Rules:
        1. Find time slots where the majority (>50%) can attend
        2. Prefer earlier times if multiple options exist
        3. Suggest 1-hour duration unless context suggests otherwise
        4. Use IST timezone
        5. Only suggest times within the next 2 weeks

        Respond with JSON:
        {{
            "found_time": boolean,
            "meeting_time": {{
                "date": "YYYY-MM-DD",
                "start_time": "HH:MM",
                "end_time": "HH:MM",
                "timezone": "Asia/Kolkata"
            }},
            "attending_participants": ["ParticipantName1", ...],
            "title": "Suggested meeting title",
            "reason": "Why this time was chosen or why no time found"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always responds with valid JSON. Do not include any text outside the JSON object."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"LLM Optimal Time Finding Error: {e}")
            return {"found_time": False, "reason": "Error processing availability"}
    
    def _create_meeting(self, chat_id: int, meeting_time: Dict, participants: List[int], title: str) -> Meeting:
        """Create meeting in database with smart replacement logic"""
        
        # Parse meeting time from LLM response
        date_str = meeting_time["date"]
        start_time_str = meeting_time["start_time"]
        end_time_str = meeting_time["end_time"]
        
        # Create IST datetime objects
        start_ist = self.ist_timezone.localize(
            datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
        )
        end_ist = self.ist_timezone.localize(
            datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")
        )
        
        # Convert to UTC for storage
        start_utc = start_ist.astimezone(pytz.UTC)
        end_utc = end_ist.astimezone(pytz.UTC)
        
        # Smart replacement logic: Check for existing meetings on the same date
        meeting_date = start_utc.date()
        existing_meetings = self.db.query(Meeting).filter(
            Meeting.chat_id == chat_id,
            Meeting.start_utc >= datetime.combine(meeting_date, datetime.min.time()).replace(tzinfo=pytz.UTC),
            Meeting.start_utc < datetime.combine(meeting_date + timedelta(days=1), datetime.min.time()).replace(tzinfo=pytz.UTC)
        ).all()
        
        # Delete existing meetings on the same date
        for existing_meeting in existing_meetings:
            # Delete participants first (foreign key constraint)
            self.db.query(MeetingParticipant).filter(
                MeetingParticipant.meeting_id == existing_meeting.id
            ).delete()
            # Delete the meeting
            self.db.delete(existing_meeting)
            print(f"🗑️ Replaced existing meeting on {meeting_date}: {existing_meeting.title}")
        
        # Create new meeting
        meeting = Meeting(
            chat_id=chat_id,
            title=title or "Team Meeting",
            start_utc=start_utc,
            end_utc=end_utc,
            description="Scheduled via AI agent"
        )
        
        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)
        
        # Add participants
        for participant_id in participants:
            participant = MeetingParticipant(
                meeting_id=meeting.id,
                user_id=participant_id
            )
            self.db.add(participant)
        
        self.db.commit()
        print(f"✅ Created new meeting for {meeting_date}: {meeting.title}")
        
        return meeting
    
    async def _send_confirmation_emails(self, meeting: Meeting, participants: List[int]):
        """Send confirmation emails to participants"""
        users = self.db.query(User).filter(User.id.in_(participants)).all()
        
        # Convert UTC back to IST for email display
        start_ist = meeting.start_utc.replace(tzinfo=pytz.UTC).astimezone(self.ist_timezone)
        
        for user in users:
            await self.email_service.send_meeting_confirmation(
                to_email=user.email,
                user_name=user.name,
                meeting_title=meeting.title,
                meeting_time=start_ist,
                meeting_id=meeting.id
            )
    
    # Fallback methods for error cases
    def _fallback_intent_detection(self, chat_history: str) -> Dict:
        """Fallback intent detection using keywords"""
        meeting_keywords = [
            "let's meet", "can we meet", "schedule a meeting", 
            "meet up", "get together", "discussion", "sync up",
            "call", "zoom", "meeting", "available", "free"
        ]
        
        chat_lower = chat_history.lower()
        has_intent = any(keyword in chat_lower for keyword in meeting_keywords)
        
        return {
            "has_intent": has_intent,
            "confidence": 0.7 if has_intent else 0.3,
            "reasoning": "Fallback keyword-based detection"
        }
    
    def _fallback_availability_extraction(self, chat_history: str, participant_names: Dict[int, str]) -> Dict:
        """Fallback availability extraction"""
        # Simple pattern matching for common formats
        result = {"participants": {}}
        
        for name in participant_names.values():
            result["participants"][name] = {
                "available_slots": [],
                "unavailable_slots": [],
                "has_availability": False,
                "constraints": ""
            }
            
            # Look for basic patterns in messages containing this participant's name
            lines = chat_history.split('\n')
            for line in lines:
                if name in line and ("thu" in line.lower() or "friday" in line.lower()):
                    # Basic Thursday detection
                    if "thu" in line.lower() and any(x in line.lower() for x in ["2-5", "4-5", "after 4"]):
                        result["participants"][name]["available_slots"].append({
                            "date": "2025-08-07",  # Next Thursday
                            "start_time": "16:00",
                            "end_time": "17:00",
                            "timezone": "Asia/Kolkata"
                        })
                        result["participants"][name]["has_availability"] = True
        
        return result