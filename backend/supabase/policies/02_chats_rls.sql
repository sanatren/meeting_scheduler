-- Row Level Security policies for chats table
-- Purpose: Control access to chat data

-- Enable RLS on chats table
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;

-- Allow all authenticated users to view chats
CREATE POLICY "Authenticated users can view chats" ON public.chats
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Allow authenticated users to create chats
CREATE POLICY "Authenticated users can create chats" ON public.chats
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Allow chat creators to update their own chats
CREATE POLICY "Chat creators can update own chats" ON public.chats
    FOR UPDATE
    USING (created_by = (SELECT id FROM public.users WHERE email = auth.email()));

-- Allow chat creators to delete their own chats (soft delete)
CREATE POLICY "Chat creators can delete own chats" ON public.chats
    FOR DELETE
    USING (created_by = (SELECT id FROM public.users WHERE email = auth.email()));
