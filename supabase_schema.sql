-- 1. Prompts (User-specific Custom Prompts)
CREATE TABLE IF NOT EXISTS prompts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    type TEXT NOT NULL, -- 'product_name' OR 'keyword'
    title TEXT,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Jobs (Task History)
CREATE TABLE IF NOT EXISTS jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'pending', 
    input_file_path TEXT NOT NULL,
    output_file_path TEXT,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    meta_data JSONB
);

-- Enable RLS (Row Level Security)
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY "Users can select their own prompts" ON prompts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own prompts" ON prompts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own prompts" ON prompts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own prompts" ON prompts FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can select their own jobs" ON jobs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own jobs" ON jobs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own jobs" ON jobs FOR UPDATE USING (auth.uid() = user_id);
