import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        self.from_email = os.getenv("FROM_EMAIL", "meetings@propvivo.com")
    
    async def send_meeting_confirmation(self, to_email: str, user_name: str, 
                                      meeting_title: str, meeting_time: datetime, 
                                      meeting_id: int):
        """Send meeting confirmation email"""
        
        # Convert UTC to IST for display
        ist = pytz.timezone('Asia/Kolkata')
        meeting_time_ist = meeting_time.astimezone(ist)
        
        # Improve deliverability with better subject and content
        subject = f"Team Meeting Scheduled - {meeting_time_ist.strftime('%b %d')}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin: 0;">📅 Meeting Invitation</h1>
                    <p style="color: #666; margin: 5px 0;">PropVivo Team Collaboration</p>
                </div>
                
                <p>Hi {user_name},</p>
                
                <p>You're invited to a team meeting scheduled through our AI assistant:</p>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin: 25px 0; text-align: center;">
                    <h2 style="margin: 0 0 15px 0; color: white;">{meeting_title}</h2>
                    <p style="font-size: 18px; margin: 10px 0; color: #f0f0f0;">
                        📅 {meeting_time_ist.strftime('%A, %B %d, %Y')}<br>
                        🕐 {meeting_time_ist.strftime('%I:%M %p')} IST
                    </p>
                    <p style="font-size: 14px; margin: 10px 0; color: #e0e0e0;">Meeting ID: #{meeting_id}</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0;">
                    <p style="margin: 0;"><strong>✅ Action Required:</strong> Please confirm your attendance</p>
                </div>
                
                <p>This meeting was automatically scheduled based on everyone's availability from the team chat.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #666; font-size: 14px;">
                        Best regards,<br>
                        <strong>PropVivo AI Meeting Scheduler</strong><br>
                        <em>Making team coordination effortless</em>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.sg.send(message)
            print(f"📧 Email sent to {to_email}")
            print(f"   Status: {response.status_code}")
            print(f"   Message ID: {response.headers.get('X-Message-Id', 'N/A')}")
            print(f"   Subject: {subject}")
            
            if response.status_code == 202:
                print(f"   ✅ Successfully queued for delivery")
            else:
                print(f"   ⚠️  Unexpected status code: {response.status_code}")
                
            return True
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            print(f"   Error type: {type(e).__name__}")
            return False
    
    async def send_follow_up_request(self, to_email: str, user_name: str, 
                                   chat_id: int, missing_info: str):
        """Send follow-up email for missing availability"""
        
        subject = "Availability Needed for Group Meeting"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Meeting Scheduling - Action Needed</h2>
                
                <p>Hello {user_name},</p>
                
                <p>The group is trying to schedule a meeting, but we need your availability information.</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Please provide your availability:</strong></p>
                    <p>{missing_info}</p>
                </div>
                
                <p>Please reply to this email or update your availability in the chat.</p>
                
                <p>Best regards,<br>
                PropVivo Meeting Scheduler</p>
            </div>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.sg.send(message)
            print(f"Follow-up email sent to {to_email}: {response.status_code}")
            return True
        except Exception as e:
            print(f"Error sending follow-up email: {e}")
            return False
