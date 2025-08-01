-- Chats table schema for PropVivo Meeting Scheduler
-- Purpose: Store group chat information

CREATE TABLE IF NOT EXISTS public.chats (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES public.users(id),
    is_active BOOLEAN DEFAULT TRUE,
    type VARCHAR(50) DEFAULT 'group' CHECK (type IN ('group', 'direct'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS chats_created_at_idx ON public.chats (created_at);
CREATE INDEX IF NOT EXISTS chats_created_by_idx ON public.chats (created_by);
CREATE INDEX IF NOT EXISTS chats_is_active_idx ON public.chats (is_active);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_chats_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chats_updated_at_trigger
    BEFORE UPDATE ON public.chats
    FOR EACH ROW
    EXECUTE FUNCTION update_chats_updated_at();
