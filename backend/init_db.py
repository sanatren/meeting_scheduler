from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Chat, Message
from datetime import datetime

def init_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if we already have data
        if db.query(User).count() > 0:
            print("Database already initialized")
            return
        
        # Create users
        users = [
            User(name="Alice", email="alice@example.com"),
            User(name="Bob", email="bob@example.com"),
            User(name="Charlie", email="charlie@example.com"),
            User(name="Diana", email="diana@example.com")
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        # Create chat
        chat = Chat(title="Project Planning Discussion")
        db.add(chat)
        db.commit()
        
        # Create sample messages
        messages = [
            {
                "chat_id": chat.id,
                "user_id": users[0].id,
                "text": "Let's meet this week to discuss the project timeline."
            },
            {
                "chat_id": chat.id,
                "user_id": users[1].id,
                "text": "I'm free Thursday 2-5 PM IST and Friday morning."
            },
            {
                "chat_id": chat.id,
                "user_id": users[2].id,
                "text": "Thursday after 4 works for me; Friday I'm out of office."
            },
            {
                "chat_id": chat.id,
                "user_id": users[3].id,
                "text": "Thursday 4-5 PM IST works perfectly for me!"
            },
            {
                "chat_id": chat.id,
                "user_id": users[0].id,
                "text": "Great! Thursday 4-5 PM IST it is. Let's schedule it."
            }
        ]
        
        for msg_data in messages:
            message = Message(**msg_data)
            db.add(message)
        
        db.commit()
        
        print("Database initialized successfully!")
        print(f"Created chat with ID: {chat.id}")
        print(f"Created users: Alice, Bob, Charlie, Diana")
        print(f"Created {len(messages)} sample messages")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
