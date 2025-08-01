
-- Purpose: Store chat messages with user and chat references

CREATE TABLE IF NOT EXISTS public.messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX messages_chat_id_idx ON public.messages (chat_id);
CREATE INDEX messages_user_id_idx ON public.messages (user_id);
CREATE INDEX messages_created_at_idx ON public.messages (created_at);
CREATE INDEX messages_chat_created_idx ON public.messages (chat_id, created_at DESC);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_messages_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    IF NEW.text IS DISTINCT FROM OLD.text THEN
        NEW.is_edited = TRUE;
        NEW.edited_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_messages_updated_at_trigger
    BEFORE UPDATE ON public.messages
    FOR EACH ROW
    EXECUTE FUNCTION update_messages_updated_at();
