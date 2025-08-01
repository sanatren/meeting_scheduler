-- Row Level Security policies for meeting_participants table
-- Purpose: Control access to meeting participant relationships

-- Enable RLS on meeting_participants table
ALTER TABLE public.meeting_participants ENABLE ROW LEVEL SECURITY;

-- Allow participants to view their own participation
CREATE POLICY "Users can view their own participation" ON public.meeting_participants
    FOR SELECT
    USING (user_id = (SELECT id FROM public.users WHERE email = auth.email()));

-- Allow meeting creators to add participants
CREATE POLICY "Meeting creators can add participants" ON public.meeting_participants
    FOR INSERT
    WITH CHECK (
        meeting_id IN (
            SELECT id FROM public.meetings 
            WHERE scheduled_by = (SELECT id FROM public.users WHERE email = auth.email())
        )
    );

-- Allow participants to update their own response
CREATE POLICY "Participants can update own response" ON public.meeting_participants
    FOR UPDATE
    USING (user_id = (SELECT id FROM public.users WHERE email = auth.email()))
    WITH CHECK (user_id = (SELECT id FROM public.users WHERE email = auth.email()));

-- Allow meeting creators to remove participants
CREATE POLICY "Meeting creators can remove participants" ON public.meeting_participants
    FOR DELETE
    USING (
        meeting_id IN (
            SELECT id FROM public.meetings 
            WHERE scheduled_by = (SELECT id FROM public.users WHERE email = auth.email())
        )
    );

-- Allow participants to view all participants of meetings they're in
CREATE POLICY "Users can view all participants of their meetings" ON public.meeting_participants
    FOR SELECT
    USING (
        meeting_id IN (
            SELECT meeting_id 
            FROM public.meeting_participants 
            WHERE user_id = (SELECT id FROM public.users WHERE email = auth.email())
        )
    );
