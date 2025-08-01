-- Master setup script for PropVivo Meeting Scheduler on Supabase
-- Purpose: Complete database setup with schemas, RLS, and sample data
-- Usage: Run this script in Supabase SQL Editor

-- Step 1: Create all tables
\i schemas/01_users.sql
\i schemas/02_chats.sql
\i schemas/03_messages.sql
\i schemas/04_meetings.sql
\i schemas/05_meeting_participants.sql

-- Step 2: Enable Row Level Security
\i policies/01_users_rls.sql
\i policies/02_chats_rls.sql
\i policies/03_messages_rls.sql
\i policies/04_meetings_rls.sql
\i policies/05_meeting_participants_rls.sql

-- Step 3: Create utility functions
\i functions/utility_functions.sql

-- Step 4: Insert sample data (optional for testing)
-- \i seeds/01_sample_data.sql

-- Step 5: Verify setup
SELECT 
    'Users table created: ' || COUNT(*) as users_count,
    'Chats table created: ' || COUNT(*) as chats_count,
    'Messages table created: ' || COUNT(*) as messages_count,
    'Meetings table created: ' || COUNT(*) as meetings_count,
    'Meeting participants table created: ' || COUNT(*) as participants_count
FROM (
    SELECT COUNT(*) FROM public.users
) u, (
    SELECT COUNT(*) FROM public.chats
) c, (
    SELECT COUNT(*) FROM public.messages
) m, (
    SELECT COUNT(*) FROM public.meetings
) mt, (
    SELECT COUNT(*) FROM public.meeting_participants
) mp;
