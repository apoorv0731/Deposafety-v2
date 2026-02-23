# Cloudflare R2 Configuration
# Free Tier: 10GB storage, 10M reads/month, 1M writes/month

# ============================================
# BUCKET CONFIGURATION
# ============================================

# Create bucket via Wrangler CLI:
# wrangler r2 bucket create deposafety-uploads

# Or via Cloudflare Dashboard:
# 1. Go to R2 > Create bucket
# 2. Name: deposafety-uploads
# 3. Location: Automatic
# 4. Storage class: Standard

# ============================================
# CORS CONFIGURATION
# ============================================

# Apply CORS via Wrangler:
# wrangler r2 bucket cors set deposafety-uploads --cors-rules='[
#   {
#     "AllowedOrigins": ["https://deposafety.vercel.app", "http://localhost:3000"],
#     "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
#     "AllowedHeaders": ["*"],
#     "ExposeHeaders": ["ETag"],
#     "MaxAgeSeconds": 3600
#   }
# ]'

# CORS JSON for Dashboard:
cat > r2-cors.json << 'EOF'
[
  {
    "AllowedOrigins": [
      "https://deposafety.vercel.app",
      "https://*.vercel.app",
      "http://localhost:3000",
      "http://localhost:3001"
    ],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
    "MaxAgeSeconds": 3600
  }
]
EOF

# ============================================
# PUBLIC ACCESS (OPTIONAL)
# ============================================

# For public file access, enable custom domain:
# 1. R2 > deposafety-uploads > Settings
# 2. Connect custom domain: files.deposafety.com
# 3. Or use public R2.dev URL (limited)

# ============================================
# LIFECYCLE POLICY (FREE TIER OPTIMIZATION)
# ============================================

# Delete old temp files after 7 days:
# wrangler r2 bucket lifecycle add deposafety-uploads --name cleanup-temp --prefix "temp/" --days 7

# ============================================
# API CREDENTIALS TEMPLATE
# ============================================

# Create API Token:
# 1. Cloudflare Dashboard > My Profile > API Tokens
# 2. Create Token > Custom token
# 3. Permissions:
#    - Account: Cloudflare R2:Edit
#    - Zone: (none needed)
# 4. Account Resources: Include - Your Account
# 5. TTL: No expiration (or set as needed)

# Required environment variables:
# R2_ACCOUNT_ID=your_cloudflare_account_id
# R2_ACCESS_KEY_ID=your_r2_access_key
# R2_SECRET_ACCESS_KEY=your_r2_secret_key
# R2_BUCKET_NAME=deposafety-uploads
# R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
# R2_PUBLIC_URL=https://files.deposafety.com (or your custom domain)
