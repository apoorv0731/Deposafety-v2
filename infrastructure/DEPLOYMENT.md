# DepoSafety V2 - Deployment Guide

Complete deployment infrastructure for free tier hosting.

## 📁 Infrastructure Structure

```
infrastructure/
├── railway.json              # Railway deployment config
├── vercel.json               # Vercel deployment config
├── docker-compose.yml        # Local development stack
├── Dockerfile                # Backend container (in backend/)
├── setup.sh                  # One-command local setup
├── deploy.sh                 # Deployment script
├── r2-config.sh              # Cloudflare R2 setup
├── .env.r2.template          # R2 credentials template
├── supabase/
│   ├── schema.sql            # Database schema
│   └── migrations/
│       ├── 001_initial_schema.sql
│       ├── 002_add_rls_policies.sql
│       └── 003_add_functions.sql
└── github/
    └── workflows/
        ├── backend.yml       # Backend CI/CD
        ├── frontend.yml      # Frontend CI/CD
        ├── database.yml      # Database migrations
        └── security.yml      # Security scanning
```

---

## 🚀 Quick Start

### 1. Local Development Setup

```bash
cd infrastructure
./setup.sh
```

This will:
- Check prerequisites (Docker, Node.js)
- Create environment files
- Start PostgreSQL and Redis
- Install dependencies

### 2. Manual Configuration

Update these files with your credentials:

**`backend/.env`**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_key
R2_SECRET_ACCESS_KEY=your_secret
R2_BUCKET_NAME=deposafety-uploads

JWT_SECRET=your_random_secret
```

**`frontend/.env.local`**
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

---

## 🛤️ Railway Deployment (Backend)

### Setup

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Create Project**
   ```bash
   cd backend
   railway init --name deposafety-api
   ```

4. **Add PostgreSQL**
   ```bash
   railway add --database postgres
   ```

5. **Set Environment Variables**
   ```bash
   railway variables set JWT_SECRET=your_secret
   railway variables set SUPABASE_URL=your_url
   railway variables set SUPABASE_SERVICE_KEY=your_key
   railway variables set R2_ENDPOINT=your_endpoint
   railway variables set R2_ACCESS_KEY_ID=your_key
   railway variables set R2_SECRET_ACCESS_KEY=your_secret
   railway variables set R2_BUCKET_NAME=deposafety-uploads
   ```

6. **Deploy**
   ```bash
   railway up
   ```

### Free Tier Limits
- 500 hours/month (sufficient for 1 service)
- 1 GB RAM, 1 vCPU
- 1 GB disk
- Custom domains

---

## ▲ Vercel Deployment (Frontend)

### Setup

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   vercel env add NEXT_PUBLIC_SUPABASE_URL
   vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
   ```

### Free Tier Limits
- 100 GB bandwidth/month
- 6,000 build minutes/month
- Serverless functions (Hobby tier)
- Preview deployments

---

## 🗄️ Supabase Setup

### 1. Create Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Choose region closest to your users (Singapore for Asia)
4. Save database password securely

### 2. Apply Schema

**Option A: Via Dashboard SQL Editor**
1. Go to SQL Editor
2. Copy contents of `supabase/schema.sql`
3. Run the SQL

**Option B: Via CLI**
```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link project
supabase link --project-ref your_project_ref

# Push migrations
supabase db push
```

### 3. Get API Keys

1. Go to Project Settings > API
2. Copy:
   - `anon public` → Frontend
   - `service_role secret` → Backend (keep secure!)

### Free Tier Limits
- 500 MB database
- 1 GB file storage
- 2 GB bandwidth
- 50,000 monthly active users

---

## ☁️ Cloudflare R2 Setup

### 1. Create Bucket

```bash
# Install Wrangler
npm install -g wrangler

# Login
wrangler login

# Create bucket
wrangler r2 bucket create deposafety-uploads
```

### 2. Configure CORS

```bash
wrangler r2 bucket cors set deposafety-uploads --cors-rules='[
  {
    "AllowedOrigins": ["https://deposafety.vercel.app", "http://localhost:3000"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]'
```

### 3. Create API Token

1. Go to Cloudflare Dashboard > My Profile > API Tokens
2. Create Token > Custom token
3. Permissions:
   - Account: Cloudflare R2:Edit
4. Copy Account ID from dashboard sidebar

### 4. Environment Variables

```env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_token_id
R2_SECRET_ACCESS_KEY=your_token_secret
R2_BUCKET_NAME=deposafety-uploads
R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://files.yourdomain.com
```

### Free Tier Limits
- 10 GB storage
- 10 million reads/month
- 1 million writes/month
- No egress fees!

---

## 🔐 GitHub Actions Secrets

Add these to your GitHub repository (Settings > Secrets and variables > Actions):

### Backend Deployment
```
RAILWAY_TOKEN=your_railway_token
```

### Frontend Deployment
```
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_org_id
VERCEL_PROJECT_ID=your_project_id
```

### Database
```
SUPABASE_ACCESS_TOKEN=your_access_token
SUPABASE_PROJECT_REF=your_project_ref
```

### Environment Variables
```
NEXT_PUBLIC_API_URL=https://deposafety-api.up.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

---

## 📊 Monitoring & Logs

### Railway
```bash
railway logs        # View logs
railway status      # Check status
railway open        # Open dashboard
```

### Vercel
```bash
vercel logs        # View logs
vercel --version   # Check version
```

### Supabase
- Dashboard: https://app.supabase.com
- Real-time logs in SQL Editor

---

## 🔄 CI/CD Workflows

### Automatic Deployments

| Event | Action |
|-------|--------|
| Push to `main` | Deploy to production |
| Push to `develop` | Run tests, build check |
| Pull Request | Run tests, lint, type check |
| Weekly | Security scan |

### Manual Triggers

```bash
# Deploy backend only
./deploy.sh --backend

# Deploy frontend only
./deploy.sh --frontend

# Deploy both
./deploy.sh --all
```

---

## 🛠️ Troubleshooting

### Railway

**Build fails:**
```bash
railway logs --follow
```

**Out of memory:**
- Reduce `NODE_OPTIONS=--max-old-space-size=512`
- Use `npm ci --production` in Dockerfile

### Vercel

**Build timeout:**
- Increase function timeout in `vercel.json`
- Optimize build process

**Environment variables not loading:**
- Ensure `NEXT_PUBLIC_` prefix for client-side vars
- Redeploy after changing env vars

### Supabase

**RLS policy blocking queries:**
```sql
-- Temporarily disable RLS for debugging (NOT for production!)
ALTER TABLE table_name DISABLE ROW LEVEL SECURITY;
```

**Connection issues:**
- Check IP allowlist in Supabase dashboard
- Verify connection string format

### R2

**CORS errors:**
- Verify CORS configuration matches frontend origin
- Check `AllowedHeaders` includes all required headers

---

## 💰 Cost Optimization (Free Tier)

### Railway
- Use 1 service (monolith instead of microservices)
- Enable sleep mode for preview deployments
- Use external database (Supabase) instead of Railway Postgres

### Vercel
- Optimize images at build time
- Use static generation where possible
- Limit serverless function execution time

### Supabase
- Add indexes for frequent queries
- Use connection pooling (PgBouncer)
- Archive old data periodically

### R2
- Compress images before upload
- Use lifecycle rules to delete temp files
- Cache frequently accessed files at edge

---

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Cloudflare R2 Docs](https://developers.cloudflare.com/r2)
