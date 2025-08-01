# Supabase Setup for PropVivo Meeting Scheduler

This directory contains all SQL schemas, RLS policies, and setup scripts for the PropVivo AI Meeting Scheduler backend.

## 📁 Directory Structure

```
supabase/
├── schemas/                    # Database table schemas
│   ├── 01_users.sql           # Users table with triggers
│   ├── 02_chats.sql           # Chats table
│   ├── 03_messages.sql        # Messages table
│   ├── 04_meetings.sql        # Meetings table
│   └── 05_meeting_participants.sql  # Meeting participants junction table
├── policies/                  # Row Level Security policies
│   ├── 01_users_rls.sql       # Users RLS policies
│   ├── 02_chats_rls.sql       # Chats RLS policies
│   ├── 03_messages_rls.sql    # Messages RLS policies
│   ├── 04_meetings_rls.sql    # Meetings RLS policies
│   └── 05_meeting_participants_rls.sql  # Meeting participants RLS policies
├── seeds/                     # Sample data for testing
│   └── 01_sample_data.sql     # Initial test data
├── functions/                 # Database utility functions
│   └── utility_functions.sql  # Helper functions
└── setup_supabase.sql         # Master setup script
```

## 🚀 Quick Setup

### Option 1: Complete Setup (Recommended)
1. Open Supabase SQL Editor
2. Copy contents of `setup_supabase.sql`
3. Run the entire script

### Option 2: Step-by-Step Setup
1. **Create Tables**: Run schemas in order (01-05)
2. **Enable RLS**: Run policies in order (01-05)
3. **Add Functions**: Run `functions/utility_functions.sql`
4. **Add Sample Data**: Run `seeds/01_sample_data.sql` (optional)

## 🔐 Security Features

### Row Level Security (RLS)
- **Users**: Can view all profiles, update own, soft delete
- **Chats**: Participants can view, creators can modify
- **Messages**: Chat participants can view, senders can modify
- **Meetings**: Participants can view, creators can manage
- **Meeting Participants**: Participants can view/update responses

### Access Control
- All tables have RLS enabled
- Policies based on user authentication
- Soft delete for data integrity
- Time-based access restrictions

## 📊 Database Schema Overview

### Core Tables
- **users**: User profiles and authentication
- **chats**: Group chat information
- **messages**: Chat messages with full history
- **meetings**: Scheduled meetings with details
- **meeting_participants**: Meeting attendance tracking

### Key Features
- UTC timestamps with timezone support
- Automatic updated_at triggers
- Foreign key constraints with CASCADE
- Performance-optimized indexes
- Soft delete patterns

## 🔧 Utility Functions

- `get_user_id_by_email(email)` - Get user ID from email
- `is_user_in_chat(user_id, chat_id)` - Check chat membership
- `get_meeting_participants_count(meeting_id)` - Meeting attendance stats
- `get_available_meeting_slots(chat_id)` - Find available time slots
- `soft_delete_user(user_id)` - Soft delete user
- `archive_old_messages()` - Archive old messages

## 🧪 Testing

After setup, you can:
1. Query sample data: `SELECT * FROM public.users;`
2. Test RLS policies with different user contexts
3. Verify foreign key relationships
4. Test utility functions

## 📝 Notes

- All timestamps stored in UTC
- Display times converted to IST in application
- Soft delete pattern prevents data loss
- Ready for Supabase Auth integration
- Compatible with Supabase Realtime subscriptions

## 🔄 Future Enhancements

- Add user roles and permissions
- Implement chat invitations
- Add meeting recurrence patterns
- Enhanced availability checking
- Real-time notifications
- Meeting templates
