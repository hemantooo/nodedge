-- Run this SQL in your Supabase SQL Editor to create the required table

CREATE TABLE IF NOT EXISTS public.registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    full_name TEXT NOT NULL,
    enrollment_no TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    class_name TEXT NOT NULL,
    has_mac TEXT NOT NULL,
    registration_id TEXT NOT NULL UNIQUE,
    attendance TEXT DEFAULT 'Absent',
    status TEXT DEFAULT 'Pending'
);

-- Create indexes to speed up lookups
CREATE INDEX idx_registrations_enrollment_no ON public.registrations(enrollment_no);
CREATE INDEX idx_registrations_registration_id ON public.registrations(registration_id);
