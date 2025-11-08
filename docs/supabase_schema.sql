-- VexaAI Data Analyst Pro - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (if not using Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    dataset_name VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    rows INTEGER NOT NULL,
    columns INTEGER NOT NULL,
    column_info JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data versions table
CREATE TABLE IF NOT EXISTS data_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    operations_applied JSONB NOT NULL,
    rows_before INTEGER NOT NULL,
    rows_after INTEGER NOT NULL,
    columns_before INTEGER NOT NULL,
    columns_after INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analysis history table
CREATE TABLE IF NOT EXISTS analysis_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    results_preview TEXT,
    interpretation TEXT,
    execution_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data quality reports table
CREATE TABLE IF NOT EXISTS data_quality_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    report_data JSONB NOT NULL,
    quality_score FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_datasets_user_id ON datasets(user_id);
CREATE INDEX IF NOT EXISTS idx_datasets_created_at ON datasets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_versions_dataset_id ON data_versions(dataset_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_dataset_id ON analysis_history(dataset_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_quality_reports_dataset_id ON data_quality_reports(dataset_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for datasets table
DROP TRIGGER IF EXISTS update_datasets_updated_at ON datasets;
CREATE TRIGGER update_datasets_updated_at
    BEFORE UPDATE ON datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_quality_reports ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic policies - adjust based on your needs)
-- Datasets: Users can only see their own datasets
CREATE POLICY "Users can view own datasets"
    ON datasets FOR SELECT
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can insert own datasets"
    ON datasets FOR INSERT
    WITH CHECK (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own datasets"
    ON datasets FOR UPDATE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own datasets"
    ON datasets FOR DELETE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Data versions: Users can view versions of their datasets
CREATE POLICY "Users can view own data versions"
    ON data_versions FOR SELECT
    USING (
        dataset_id IN (
            SELECT id FROM datasets 
            WHERE user_id = current_setting('request.jwt.claims', true)::json->>'sub'
        )
    );

-- Analysis history: Users can view their own analysis
CREATE POLICY "Users can view own analysis"
    ON analysis_history FOR SELECT
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Audit logs: Users can view their own audit logs
CREATE POLICY "Users can view own audit logs"
    ON audit_logs FOR SELECT
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Data quality reports: Users can view reports for their datasets
CREATE POLICY "Users can view own quality reports"
    ON data_quality_reports FOR SELECT
    USING (
        dataset_id IN (
            SELECT id FROM datasets 
            WHERE user_id = current_setting('request.jwt.claims', true)::json->>'sub'
        )
    );

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Insert sample admin user (optional - remove in production)
-- Password: admin123 (hashed with SHA-256)
-- INSERT INTO users (username, email, password_hash, role)
-- VALUES ('admin', 'admin@vexaai.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin');

COMMENT ON TABLE datasets IS 'Stores metadata about uploaded datasets';
COMMENT ON TABLE data_versions IS 'Tracks all versions and transformations of datasets';
COMMENT ON TABLE analysis_history IS 'Stores history of analyses performed';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail of all user activities';
COMMENT ON TABLE data_quality_reports IS 'Automated data quality assessment reports';
