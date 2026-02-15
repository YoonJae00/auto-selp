-- 설정 테이블 생성 (User Settings)
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) UNIQUE NOT NULL,
    
    -- 엑셀 컬럼 매핑 (사용자가 커스터마이징 가능)
    excel_column_mapping JSONB DEFAULT '{
        "original_product_name": "A",
        "refined_product_name": "B",
        "keyword": "C",
        "category": "D"
    }'::jsonb,
    
    -- API 키 정보 (암호화되어 저장)
    api_keys JSONB DEFAULT '{}'::jsonb,
    
    -- 추가 설정 (향후 확장 가능)
    preferences JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS (Row Level Security) 활성화
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 사용자는 자기 자신의 설정만 조회 가능
CREATE POLICY "Users can select their own settings" 
ON user_settings FOR SELECT 
USING (auth.uid() = user_id);

-- RLS 정책: 사용자는 자기 자신의 설정만 삽입 가능
CREATE POLICY "Users can insert their own settings" 
ON user_settings FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- RLS 정책: 사용자는 자기 자신의 설정만 업데이트 가능
CREATE POLICY "Users can update their own settings" 
ON user_settings FOR UPDATE 
USING (auth.uid() = user_id);

-- RLS 정책: 사용자는 자기 자신의 설정만 삭제 가능
CREATE POLICY "Users can delete their own settings" 
ON user_settings FOR DELETE 
USING (auth.uid() = user_id);

-- updated_at 자동 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- user_settings 테이블에 트리거 적용
DROP TRIGGER IF EXISTS update_user_settings_updated_at ON user_settings;
CREATE TRIGGER update_user_settings_updated_at
BEFORE UPDATE ON user_settings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
