-- Migration: 002_add_rls_policies.sql
-- Created: 2024-02-23
-- Description: Add Row Level Security policies

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deposits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deposit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scam_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.platform_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.files ENABLE ROW LEVEL SECURITY;

-- ============================================
-- PROFILES POLICIES
-- ============================================

-- Users can read their own profile
CREATE POLICY "Users can read own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Admins can read all profiles
CREATE POLICY "Admins can read all profiles"
    ON public.profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================
-- DEPOSITS POLICIES
-- ============================================

-- Users can read their own deposits
CREATE POLICY "Users can read own deposits"
    ON public.deposits FOR SELECT
    USING (auth.uid() = user_id);

-- Users can create their own deposits
CREATE POLICY "Users can create own deposits"
    ON public.deposits FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own pending deposits
CREATE POLICY "Users can update own pending deposits"
    ON public.deposits FOR UPDATE
    USING (auth.uid() = user_id AND status = 'pending');

-- Admins/moderators can read all deposits
CREATE POLICY "Admins can read all deposits"
    ON public.deposits FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role IN ('admin', 'moderator')
        )
    );

-- Admins/moderators can update all deposits
CREATE POLICY "Admins can update all deposits"
    ON public.deposits FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role IN ('admin', 'moderator')
        )
    );

-- ============================================
-- SCAM REPORTS POLICIES
-- ============================================

-- Anyone can read confirmed scam reports
CREATE POLICY "Anyone can read confirmed scam reports"
    ON public.scam_reports FOR SELECT
    USING (status = 'confirmed');

-- Reporters can read their own reports
CREATE POLICY "Reporters can read own reports"
    ON public.scam_reports FOR SELECT
    USING (auth.uid() = reporter_id);

-- Authenticated users can create scam reports
CREATE POLICY "Authenticated users can create scam reports"
    ON public.scam_reports FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

-- Admins/moderators can read all scam reports
CREATE POLICY "Admins can read all scam reports"
    ON public.scam_reports FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role IN ('admin', 'moderator')
        )
    );

-- Admins/moderators can update scam reports
CREATE POLICY "Admins can update scam reports"
    ON public.scam_reports FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role IN ('admin', 'moderator')
        )
    );

-- ============================================
-- PLATFORM RATINGS POLICIES
-- ============================================

-- Anyone can read platform ratings
CREATE POLICY "Anyone can read platform ratings"
    ON public.platform_ratings FOR SELECT
    TO PUBLIC
    USING (true);

-- Only admins can modify platform ratings
CREATE POLICY "Only admins can insert platform ratings"
    ON public.platform_ratings FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Only admins can update platform ratings"
    ON public.platform_ratings FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================
-- NOTIFICATIONS POLICIES
-- ============================================

-- Users can read their own notifications
CREATE POLICY "Users can read own notifications"
    ON public.notifications FOR SELECT
    USING (auth.uid() = user_id);

-- Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications"
    ON public.notifications FOR UPDATE
    USING (auth.uid() = user_id);

-- System can create notifications for any user
CREATE POLICY "System can create notifications"
    ON public.notifications FOR INSERT
    WITH CHECK (true);

-- Users can delete their own notifications
CREATE POLICY "Users can delete own notifications"
    ON public.notifications FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- FILES POLICIES
-- ============================================

-- Users can read their own files
CREATE POLICY "Users can read own files"
    ON public.files FOR SELECT
    USING (auth.uid() = user_id);

-- Users can create their own files
CREATE POLICY "Users can create own files"
    ON public.files FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own files
CREATE POLICY "Users can delete own files"
    ON public.files FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- MIGRATION RECORD
-- ============================================
INSERT INTO schema_migrations (version, description)
VALUES ('002', 'Add Row Level Security policies')
ON CONFLICT (version) DO NOTHING;
