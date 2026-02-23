-- DepoSafety V2 Database Schema
-- Free Tier Compatible (Supabase PostgreSQL)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

-- Users table (extends Supabase Auth)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User sessions for tracking
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    ip_address INET,
    user_agent TEXT,
    last_active TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- DEPOSITS & TRANSACTIONS
-- ============================================

-- Deposit records (core feature)
CREATE TABLE IF NOT EXISTS public.deposits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    
    -- Deposit details
    platform TEXT NOT NULL,
    platform_url TEXT,
    amount DECIMAL(15, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    
    -- Status tracking
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'disputed', 'resolved', 'refunded')),
    
    -- Evidence
    screenshot_url TEXT,
    transaction_id TEXT,
    payment_method TEXT,
    
    -- Verification
    verified_by UUID REFERENCES public.profiles(id),
    verified_at TIMESTAMPTZ,
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deposit history/audit log
CREATE TABLE IF NOT EXISTS public.deposit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deposit_id UUID REFERENCES public.deposits(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    performed_by UUID REFERENCES public.profiles(id),
    old_data JSONB,
    new_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SAFETY REPORTS & SCAMS
-- ============================================

-- Scam reports
CREATE TABLE IF NOT EXISTS public.scam_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    
    -- Scam details
    platform_name TEXT NOT NULL,
    platform_url TEXT,
    scam_type TEXT CHECK (scam_type IN ('phishing', 'ponzi', 'fake_exchange', 'rug_pull', 'other')),
    description TEXT NOT NULL,
    
    -- Evidence
    evidence_urls TEXT[],
    screenshot_urls TEXT[],
    
    -- Status
    status TEXT DEFAULT 'under_review' CHECK (status IN ('under_review', 'confirmed', 'false_report', 'resolved')),
    
    -- Verification
    verified_by UUID REFERENCES public.profiles(id),
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Platform safety ratings
CREATE TABLE IF NOT EXISTS public.platform_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_name TEXT UNIQUE NOT NULL,
    platform_url TEXT,
    
    -- Ratings
    trust_score INTEGER CHECK (trust_score >= 0 AND trust_score <= 100),
    user_rating DECIMAL(3, 2) CHECK (user_rating >= 0 AND user_rating <= 5),
    review_count INTEGER DEFAULT 0,
    
    -- Safety metrics
    is_verified BOOLEAN DEFAULT FALSE,
    has_ssl BOOLEAN DEFAULT FALSE,
    registration_country TEXT,
    
    -- Risk flags
    scam_reports_count INTEGER DEFAULT 0,
    is_blacklisted BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    last_checked TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- NOTIFICATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    
    type TEXT CHECK (type IN ('deposit_confirmed', 'deposit_disputed', 'scam_alert', 'system', 'verification')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    
    -- Link to related entity
    related_entity_type TEXT,
    related_entity_id UUID,
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- FILE STORAGE METADATA
-- ============================================

CREATE TABLE IF NOT EXISTS public.files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    
    -- Storage
    storage_provider TEXT DEFAULT 'r2' CHECK (storage_provider IN ('r2', 'supabase')),
    bucket_name TEXT NOT NULL,
    object_key TEXT NOT NULL,
    public_url TEXT,
    
    -- Usage
    entity_type TEXT, -- 'deposit', 'scam_report', 'avatar'
    entity_id UUID,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_deposits_user_id ON public.deposits(user_id);
CREATE INDEX IF NOT EXISTS idx_deposits_status ON public.deposits(status);
CREATE INDEX IF NOT EXISTS idx_deposits_platform ON public.deposits(platform);
CREATE INDEX IF NOT EXISTS idx_deposits_created_at ON public.deposits(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_scam_reports_status ON public.scam_reports(status);
CREATE INDEX IF NOT EXISTS idx_scam_reports_platform ON public.scam_reports(platform_name);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON public.notifications(user_id, is_read) WHERE is_read = FALSE;

CREATE INDEX IF NOT EXISTS idx_files_user_id ON public.files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_entity ON public.files(entity_type, entity_id);

-- ============================================
-- TRIGGERS
-- ============================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deposits_updated_at BEFORE UPDATE ON public.deposits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scam_reports_updated_at BEFORE UPDATE ON public.scam_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_ratings_updated_at BEFORE UPDATE ON public.platform_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
