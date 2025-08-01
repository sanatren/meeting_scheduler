-- Row Level Security policies for users table
-- Purpose: Control access to user data

-- Enable RLS on users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Allow users to read all user profiles (needed for group chats)
CREATE POLICY "Users can view all profiles" ON public.users
    FOR SELECT
    USING (true);

-- Allow users to update their own profile
CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE
    USING (auth.uid()::text = email::text);

-- Allow users to insert their own profile (during registration)
CREATE POLICY "Users can insert own profile" ON public.users
    FOR INSERT
    WITH CHECK (auth.uid()::text = email::text);

-- Prevent deletion of user profiles (soft delete instead)
CREATE POLICY "Prevent user deletion" ON public.users
    FOR DELETE
    USING (false);
