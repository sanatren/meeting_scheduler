-- Row Level Security policies for messages table
-- Purpose: Control access to chat messages

-- Enable RLS on messages table
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Allow all authenticated users to view messages in chats they're part of
CREATE POLICY "Users can view messages in their chats" ON public.messages
    FOR SELECT
    USING (
        auth.role() = 'authenticated' AND
        chat_id IN (
            SELECT DISTINCT chat_id 
            FROM public.messages 
            WHERE user_id = (SELECT id FROM public.users WHERE email = auth.email())
            UNION
            SELECT id FROM public.chats WHERE created_by = (SELECT id FROM public.users WHERE email = auth.email())
        )
    );

-- Allow authenticated users to send messages
CREATE POLICY "Authenticated users can send messages" ON public.messages
    FOR INSERT
    WITH CHECK (
        auth.role() = 'authenticated' AND
        user_id = (SELECT id FROM public.users WHERE email = auth.email())
    );

-- Allow users to update their own messages
CREATE POLICY "Users can update own messages" ON public.messages
    FOR UPDATE
    USING (user_id = (SELECT id FROM public.users WHERE email = auth.email()))
    WITH CHECK (user_id = (SELECT id FROM public.users WHERE email = auth.email()));

-- Allow users to delete their own messages
CREATE POLICY "Users can delete own messages" ON public.messages
    FOR DELETE
    USING (user_id = (SELECT id FROM public.users WHERE email = auth.email()));
