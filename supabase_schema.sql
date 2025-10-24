-- Supabase Database Schema for Content Brief Creator
-- Execute this SQL in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS clients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    client_name TEXT UNIQUE NOT NULL,
    site TEXT DEFAULT '',
    industry TEXT DEFAULT '',
    target_audience TEXT DEFAULT '',
    brand_voice TEXT DEFAULT '',
    content_goals TEXT DEFAULT '',
    restrictions JSONB DEFAULT '{
        "legal": [],
        "brand": [],
        "seo": [],
        "content_integrity": []
    }'::jsonb,
    requirements JSONB DEFAULT '{
        "word_count": null,
        "readability_score": "",
        "tone": "",
        "mandatory_mentions": [],
        "schema_required": false,
        "images_required": 0,
        "cta_required": true,
        "internal_links_min": 6
    }'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create index on client_name for faster lookups
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(client_name);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_clients_updated_at 
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your auth requirements)
CREATE POLICY "Enable all operations for authenticated users" ON clients
    FOR ALL
    USING (true)
    WITH CHECK (true);
