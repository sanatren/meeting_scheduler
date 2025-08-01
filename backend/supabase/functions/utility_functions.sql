-- Utility functions for PropVivo Meeting Scheduler
-- Purpose: Helper functions for data management and business logic

-- Function to get user ID from email
CREATE OR REPLACE FUNCTION public.get_user_id_by_email(user_email TEXT)
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT id FROM public.users WHERE email = user_email LIMIT 1);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is participant in a chat
CREATE OR REPLACE FUNCTION public.is_user_in_chat(p_user_id INTEGER, p_chat_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM public.messages 
        WHERE user_id = p_user_id AND chat_id = p_chat_id
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get meeting participants count
CREATE OR REPLACE FUNCTION public.get_meeting_participants_count(p_meeting_id INTEGER)
RETURNS TABLE (
    total_participants INTEGER,
    confirmed_count INTEGER,
    declined_count INTEGER,
    pending_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_participants,
        COUNT(*) FILTER (WHERE response = 'confirmed') as confirmed_count,
        COUNT(*) FILTER (WHERE response = 'declined') as declined_count,
        COUNT(*) FILTER (WHERE response = 'invited') as pending_count
    FROM public.meeting_participants
    WHERE meeting_id = p_meeting_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get available meeting slots for a chat
CREATE OR REPLACE FUNCTION public.get_available_meeting_slots(p_chat_id INTEGER)
RETURNS TABLE (
    slot_start TIMESTAMP WITH TIME ZONE,
    slot_end TIMESTAMP WITH TIME ZONE,
    available_users INTEGER,
    total_users INTEGER
) AS $$
BEGIN
    -- This is a simplified version - in production, use more sophisticated logic
    RETURN QUERY
    SELECT 
        NOW() + INTERVAL '1 day' as slot_start,
        NOW() + INTERVAL '1 day 1 hour' as slot_end,
        3 as available_users,
        5 as total_users;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to soft delete a user
CREATE OR REPLACE FUNCTION public.soft_delete_user(p_user_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE public.users 
    SET is_active = FALSE, updated_at = NOW()
    WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to archive old messages (older than 90 days)
CREATE OR REPLACE FUNCTION public.archive_old_messages()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- In production, you might move these to an archive table
    -- For now, we'll just return the count
    SELECT COUNT(*) INTO archived_count
    FROM public.messages
    WHERE created_at < NOW() - INTERVAL '90 days';
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
