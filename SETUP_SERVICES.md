# DepoSafety V2 - Free Tier Setup Guide

## Services to Configure (All Free Tier)

### 1. Supabase (Database + Auth)
**URL:** https://supabase.com
**Free Tier:** 500MB DB, 1GB storage, 50K MAU

**Setup Steps:**
1. Sign up with GitHub
2. Create new project
3. Get URL and anon key from Settings → API
4. Run schema.sql in SQL Editor

### 2. Cloudflare R2 (Video Storage)
**URL:** https://dash.cloudflare.com
**Free Tier:** 10GB storage, no egress fees

**Setup Steps:**
1. Sign up
2. Go to R2
3. Create bucket "deposafety-videos"
4. Create API token with R2 permissions
5. Get endpoint URL, access key, secret key

### 3. Polygon Mumbai (Blockchain)
**URL:** https://mumbai.polygonscan.com
**Free:** Testnet, free MATIC from faucet

**Setup Steps:**
1. Create wallet at https://vanity-eth.tk
2. Get MATIC from https://faucet.polygon.technology
3. Deploy contract using deploy.py
4. Save contract address

### 4. SendGrid (Email)
**URL:** https://sendgrid.com
**Free Tier:** 100 emails/day

**Setup Steps:**
1. Sign up
2. Create API key
3. Verify sender email
4. Save API key

### 5. Railway (Backend Hosting)
**URL:** https://railway.app
**Free Tier:** $5/month credit

**Setup Steps:**
1. Sign up with GitHub
2. Install CLI: npm i -g @railway/cli
3. railway login
4. railway init
5. railway up

### 6. Vercel (Frontend Hosting)
**URL:** https://vercel.com
**Free Tier:** 100GB bandwidth

**Setup Steps:**
1. Sign up with GitHub
2. Install CLI: npm i -g vercel
3. vercel login
4. cd frontend && vercel --prod

## Environment Variables

Create `.env` file in backend/:
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJ...
R2_ENDPOINT_URL=https://xxxx.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=xxxx
R2_SECRET_ACCESS_KEY=xxxx
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
WALLET_PRIVATE_KEY=xxxx
CONTRACT_ADDRESS=0x...
SENDGRID_API_KEY=SG.xxxx
```

Create `.env.local` in frontend/:
```
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

## Deployment Order

1. Supabase (database)
2. R2 (storage)
3. Deploy backend to Railway
4. Deploy frontend to Vercel
5. Polygon contract
6. Test end-to-end

## Testing

After setup, run:
```bash
cd backend
pytest tests/ -v

cd frontend
npm test
```

## Monitoring (Free)

- Railway: Built-in logs
- Vercel: Analytics dashboard
- Supabase: Dashboard metrics
- UptimeRobot: Free monitoring (https://uptimerobot.com)
