-- Migration: 003_add_functions.sql
-- Created: 2024-02-23
-- Description: Add helper functions and views

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get user's deposit statistics
CREATE OR REPLACE FUNCTION public.get_user_deposit_stats(user_uuid UUID)
RETURNS TABLE (
    total_deposits BIGINT,
    total_amount DECIMAL,
    pending_count BIGINT,
    confirmed_count BIGINT,
    disputed_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_deposits,
        COALESCE(SUM(amount), 0) as total_amount,
        COUNT(*) FILTER (WHERE status = 'pending')::BIGINT as pending_count,
        COUNT(*) FILTER (WHERE status = 'confirmed')::BIGINT as confirmed_count,
        COUNT(*) FILTER (WHERE status = 'disputed')::BIGINT as disputed_count
    FROM public.deposits
    WHERE user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to search platforms
CREATE OR REPLACE FUNCTION public.search_platforms(search_query TEXT)
RETURNS TABLE (
    id UUID,
    platform_name TEXT,
    platform_url TEXT,
    trust_score INTEGER,
    is_blacklisted BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.id,
        pr.platform_name,
        pr.platform_url,
        pr.trust_score,
        pr.is_blacklisted
    FROM public.platform_ratings pr
    WHERE 
        pr.platform_name ILIKE '%' || search_query || '%'
        OR pr.platform_url ILIKE '%' || search_query || '%'
    ORDER BY pr.trust_score DESC, pr.platform_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if platform is safe
CREATE OR REPLACE FUNCTION public.check_platform_safety(platform TEXT)
RETURNS TABLE (
    platform_name TEXT,
    trust_score INTEGER,
    is_blacklisted BOOLEAN,
    scam_reports_count INTEGER,
    risk_level TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.platform_name,
        pr.trust_score,
        pr.is_blacklisted,
        pr.scam_reports_count,
        CASE 
            WHEN pr.is_blacklisted THEN 'high'
            WHEN pr.trust_score < 30 THEN 'high'
            WHEN pr.trust_score < 60 THEN 'medium'
            ELSE 'low'
        END as risk_level
    FROM public.platform_ratings pr
    WHERE pr.platform_name ILIKE platform
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- VIEWS
-- ============================================

-- View: Recent deposits with user info
CREATE OR REPLACE VIEW public.recent_deposits AS
SELECT 
    d.*,
    p.full_name as user_name,
    p.email as user_email
FROM public.deposits d
JOIN public.profiles p ON d.user_id = p.id
ORDER BY d.created_at DESC;

-- View: High risk platforms
CREATE OR REPLACE VIEW public.high_risk_platforms AS
SELECT 
    *,
    CASE 
        WHEN is_blacklisted THEN 'blacklisted'
        WHEN trust_score < 30 THEN 'untrusted'
        WHEN scam_reports_count > 5 THEN 'suspicious'
    END as risk_category
FROM public.platform_ratings
WHERE is_blacklisted = TRUE OR trust_score < 30 OR scam_reports_count > 5;

-- View: User dashboard summary
CREATE OR REPLACE VIEW public.user_dashboard AS
SELECT 
    p.id as user_id,
    p.email,
    p.full_name,
    p.role,
    COUNT(DISTINCT d.id) as total_deposits,
    COALESCE(SUM(d.amount), 0) as total_deposited,
    COUNT(DISTINCT n.id) FILTER (WHERE n.is_read = FALSE) as unread_notifications
FROM public.profiles p
LEFT JOIN public.deposits d ON p.id = d.user_id
LEFT JOIN public.notifications n ON p.id = n.user_id
GROUP BY p.id, p.email, p.full_name, p.role;

-- ============================================
-- MIGRATION RECORD
-- ============================================
INSERT INTO schema_migrations (version, description)
VALUES ('003', 'Add helper functions and views')
ON CONFLICT (version) DO NOTHING;
