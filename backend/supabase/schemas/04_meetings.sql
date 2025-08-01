-- Meetings table schema for PropVivo Meeting Scheduler
-- Purpose: Store scheduled meeting information

CREATE TABLE IF NOT EXISTS public.meetings (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'Group Meeting',
    description TEXT,
    start_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    end_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'cancelled', 'completed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scheduled_by INTEGER REFERENCES public.users(id),
    timezone VARCHAR(50) DEFAULT 'UTC',
    location VARCHAR(255),
    meeting_url VARCHAR(500),
    notes TEXT,
    
    -- Constraints
    CONSTRAINT meetings_time_check CHECK (end_utc > start_utc)
);

-- Indexes for performance
CREATE INDEX idx_meetings_chat_id ON public.meetings (chat_id);
CREATE INDEX idx_meetings_scheduled_by ON public.meetings (scheduled_by);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_meetings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_meetings_updated_at_trigger
    BEFORE UPDATE ON public.meetings
    FOR EACH ROW
    EXECUTE FUNCTION update_meetings_updated_at();
