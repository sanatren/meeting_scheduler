
-- Purpose: Store participant relationships for meetings

CREATE TABLE IF NOT EXISTS public.meeting_participants (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER NOT NULL REFERENCES public.meetings(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    response VARCHAR(50) DEFAULT 'invited' CHECK (response IN ('invited', 'confirmed', 'declined', 'tentative')),
    responded_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    
    -- Ensure unique participant per meeting
    CONSTRAINT unique_participant_per_meeting UNIQUE (meeting_id, user_id)
);

-- Indexes for performance
CREATE INDEX idx_meeting_participants_meeting_id ON public.meeting_participants (meeting_id);
CREATE INDEX idx_meeting_participants_user_id ON public.meeting_participants (user_id);
CREATE INDEX idx_meeting_participants_response ON public.meeting_participants (response);
CREATE INDEX idx_meeting_participants_meeting_response ON public.meeting_participants (meeting_id, response);

-- Trigger to update responded_at when response changes
CREATE OR REPLACE FUNCTION update_meeting_participants_responded_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.response IS DISTINCT FROM OLD.response THEN
        NEW.responded_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_meeting_participants_responded_at_trigger
    BEFORE UPDATE ON public.meeting_participants
    FOR EACH ROW
    EXECUTE FUNCTION update_meeting_participants_responded_at();
