-- Row Level Security policies for meetings table
-- Purpose: Control access to meeting data

-- Enable RLS on meetings table
ALTER TABLE public.meetings ENABLE ROW LEVEL SECURITY;

-- Allow participants to view meetings they're part of
CREATE POLICY "Participants can view their meetings" ON public.meetings
    FOR SELECT
    USING (
        id IN (
            SELECT meeting_id 
            FROM public.meeting_participants 
            WHERE user_id = (SELECT id FROM public.users WHERE email = auth.email())
        ) OR
        chat_id IN (
            SELECT chat_id 
            FROM public.messages 
            WHERE user_id = (SELECT id FROM public.users WHERE email = auth.email())
        )
    );

-- Allow chat participants to create meetings
CREATE POLICY "Chat participants can create meetings" ON public.meetings
    FOR INSERT
    WITH CHECK (
        chat_id IN (
            SELECT DISTINCT chat_id 
            FROM public.messages 
            WHERE user_id = (SELECT id FROM public.users WHERE email = auth.email())
        )
    );

-- Allow meeting creators to update meetings
CREATE POLICY "Meeting creators can update meetings" ON public.meetings
    FOR UPDATE
    USING (scheduled_by = (SELECT id FROM public.users WHERE email = auth.email()))
    WITH CHECK (scheduled_by = (SELECT id FROM public.users WHERE email = auth.email()));

-- Allow meeting creators to delete meetings
CREATE POLICY "Meeting creators can delete meetings" ON public.meetings
    FOR DELETE
    USING (scheduled_by = (SELECT id FROM public.users WHERE email = auth.email()));
