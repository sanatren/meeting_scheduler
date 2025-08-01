# PropVivo AI Meeting Scheduler

An AI-powered web application that enables group chat with intelligent meeting scheduling capabilities.

## Features

- **Group Chat**: Real-time multi-user conversations
- **AI Scheduling Agent**: Automatically detects meeting intent and schedules based on chat history
- **Availability Extraction**: Parses natural language for availability information
- **Majority Rule Scheduling**: Finds optimal meeting times for majority of participants
- **Email Notifications**: Sends confirmation emails to all participants
- **Responsive UI**: Clean, modern interface with Tailwind CSS

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Database (via Supabase)
- **SQLAlchemy**: ORM
- **OpenAI GPT**: AI agent for intent detection and availability extraction
- **SendGrid**: Email service

### Frontend
- **HTML/CSS/JavaScript**: Vanilla JS with Tailwind CSS
- **Responsive Design**: Mobile-friendly interface

## Project Structure

```
propvivo-assignment/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utility functions
│   │   └── main.py          # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variables template
│   └── init_db.py          # Database initialization script
├── frontend/
│   ├── index.html          # Main HTML file
│   └── static/
│       └── app.js          # Frontend JavaScript
└── README.md
```

## Setup Instructions

### 1. Environment Setup

1. **Clone the repository**
2. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

### 2. Database Setup

1. **Set up PostgreSQL database** (or use Supabase)
2. **Update DATABASE_URL in .env**
3. **Initialize database:**
   ```bash
   python init_db.py
   ```

### 3. API Keys Setup

1. **Get OpenAI API key** from [OpenAI Platform](https://platform.openai.com)
2. **Get SendGrid API key** from [SendGrid](https://sendgrid.com)
3. **Add keys to .env file**

### 4. Run the Application

1. **Start the backend server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open frontend:**
   - Open `frontend/index.html` in your browser
   - Or serve it via a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 3000
     ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## API Endpoints

### Messages
- `POST /api/messages` - Send a new message
- `GET /api/messages?chat_id={id}` - Get chat messages

### Scheduling
- `POST /api/schedule` - Trigger AI scheduling agent

### Meetings
- `GET /api/meetings/{id}` - Get meeting details
- `POST /api/meetings/{id}/confirm` - Confirm meeting attendance

## Usage Example

1. **Start chatting** in the group chat
2. **Mention meeting times** naturally (e.g., "I'm free Thursday 2-5 PM")
3. **Click "Schedule Meeting"** to trigger the AI agent
4. **Receive confirmation** via email and in-app notification

## Development

### Adding New Features
- Database models: Add to `backend/app/models/`
- API endpoints: Add to `backend/app/routes/`
- Business logic: Add to `backend/app/services/`
- Frontend: Update `frontend/` files

### Testing
- Use the built-in FastAPI docs at `/docs` for API testing
- Check browser console for frontend debugging

## Success Criteria Met

✅ **Preloaded chats visible on UI**
✅ **Real-time chat functionality**
✅ **Agent schedules based on chat if majority agrees**
✅ **Confirmation email sent to all participants**
✅ **Database-backed multi-user chat**
✅ **Detect intent & availability**
✅ **Propose optimal meeting time**
✅ **Follow-up questions for missing info**

## Next Steps

- [ ] Add real-time WebSocket support
- [ ] Implement meeting rescheduling
- [ ] Add calendar integration
- [ ] Enhance AI agent with better NLP
- [ ] Add user authentication
- [ ] Implement meeting reminders
