-- Sample data for PropVivo Meeting Scheduler
-- Purpose: Populate database with initial test data

-- Insert sample users
INSERT INTO public.users (name, email, timezone) VALUES 
('Alice Johnson', 'alice@propvivo.com', 'Asia/Kolkata'),
('Bob Smith', 'bob@propvivo.com', 'Asia/Kolkata'),
('Charlie Brown', 'charlie@propvivo.com', 'Asia/Kolkata'),
('Diana Prince', 'diana@propvivo.com', 'Asia/Kolkata'),
('Eve Wilson', 'eve@propvivo.com', 'Asia/Kolkata');

-- Insert sample chat
INSERT INTO public.chats (title, description, created_by) VALUES 
('Project Planning Discussion', 'Weekly sync for Q3 project deliverables', 1);

-- Insert sample messages for the chat
INSERT INTO public.messages (chat_id, user_id, text) VALUES 
(1, 1, 'Hey team! Let''s schedule a meeting this week to discuss our Q3 project timeline and deliverables.'),
(1, 2, 'Sounds good! I''m available Thursday 2-5 PM IST and Friday morning 9 AM - 12 PM IST.'),
(1, 3, 'Thursday after 4 PM works perfectly for me. Friday I have a client call so I''m unavailable.'),
(1, 4, 'Thursday 4-5 PM IST works great for me! I can make it.'),
(1, 5, 'Thursday 4-5 PM IST works for me too. I''ll join.'),
(1, 1, 'Perfect! So we have consensus for Thursday 4-5 PM IST. Let''s schedule it.'),
(1, 2, 'Great! Looking forward to the discussion. Should we prepare any specific agenda items?'),
(1, 3, 'I can prepare the project timeline update and current blockers.'),
(1, 4, 'I''ll bring the resource allocation summary.'),
(1, 1, 'Excellent! I''ll send the calendar invite shortly.');

-- Insert sample meeting
INSERT INTO public.meetings (chat_id, title, description, start_utc, end_utc, scheduled_by, timezone, location) VALUES 
(1, 'Q3 Project Planning Sync', 'Weekly team sync to discuss Q3 deliverables, timeline, and resource allocation', 
 '2025-08-07T10:30:00+00:00', '2025-08-07T11:30:00+00:00', 1, 'Asia/Kolkata', 'Conference Room A / Google Meet');

-- Insert meeting participants
INSERT INTO public.meeting_participants (meeting_id, user_id, response) VALUES 
(1, 1, 'confirmed'),
(1, 2, 'confirmed'),
(1, 3, 'confirmed'),
(1, 4, 'confirmed'),
(1, 5, 'confirmed');
