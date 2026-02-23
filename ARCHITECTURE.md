# DepoSafety V2 - Full Application Architecture

## Overview
Forensic-grade 3D capture with full evidence chain, deployed on free tier infrastructure.

## Street-Smart Free Tier Strategy

### Backend (Railway + Supabase Free Tier)
- **Railway**: $5/month free credit (hosting FastAPI)
- **Supabase**: 500MB database, 1GB storage (PostgreSQL + Auth)
- **Cloudflare R2**: 10GB free (S3-compatible storage)
- **Porkbun**: $1/year domains (cheapest)

### 3D Processing (Free GPU Options)
- **Google Colab**: Free Tesla T4 GPU (for 3DGS training)
- **Kaggle**: Free GPU hours
- **Local processing**: Fallback for small models

### Blockchain (Free Testnets)
- **Polygon Mumbai**: Free testnet for anchoring hashes
- **Ethereum Goerli**: Alternative (being deprecated)

### Frontend (Free Hosting)
- **Vercel**: Free React/Next.js hosting
- **Cloudflare Pages**: Alternative

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│  FastAPI Backend │────▶│  PostgreSQL DB  │
│  (React/Vercel) │     │   (Railway)      │     │  (Supabase)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  Cloudflare R2  │     │  ML Pipeline     │
│  (Video Storage)│     │  (Colab/Local)   │
└─────────────────┘     └──────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ 3DGS Model Gen   │
                        │ (Gaussian Splats)│
                        └──────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ Blockchain Anchor│
                        │ (Polygon Mumbai) │
                        └──────────────────┘
```

## Features V2

### Core (MVP Complete)
- [x] User auth (JWT)
- [x] Property management
- [x] Video upload with SHA-256 hash
- [x] Evidence reports

### New Features
- [ ] Real 3D Gaussian Splatting pipeline
- [ ] Interactive 3D viewer (Three.js)
- [ ] Blockchain hash anchoring
- [ ] PDF report generation
- [ ] Email notifications (SendGrid free)
- [ ] SMS alerts (Twilio trial)
- [ ] Mobile-responsive web app
- [ ] Offline mode (PWA)

## Timeline (10 Hours)

| Hour | Task |
|------|------|
| 0-1 | Setup infrastructure, Railway, Supabase |
| 1-2 | Backend API expansion |
| 2-3 | 3DGS pipeline (Colab integration) |
| 3-4 | Frontend web app |
| 4-5 | Blockchain integration |
| 5-6 | Testing & bug fixes |
| 6-7 | Simulation runs (20x) |
| 7-8 | Bug fixes & re-runs |
| 8-9 | Documentation & deployment |
| 9-10 | Final testing & handoff |

## Sub-Agents

1. **backend-architect** - FastAPI + Supabase
2. **frontend-developer** - React + Three.js
3. **ml-engineer** - 3DGS pipeline
4. **blockchain-dev** - Polygon integration
5. **qa-tester** - Test scenarios
6. **devops-engineer** - Deployment
7. **security-auditor** - Security review
8. **ui-designer** - Interface design
9. **docs-writer** - Documentation
10. **simulation-runner** - Load testing

## Free Tier Limits

| Service | Free Limit |
|---------|-----------|
| Railway | $5/month |
| Supabase | 500MB DB, 1GB storage |
| Cloudflare R2 | 10GB/month |
| Vercel | 100GB bandwidth |
| Polygon Mumbai | Unlimited (testnet) |
| SendGrid | 100 emails/day |
| Twilio | $15.50 trial credit |

## Deployment

### Railway (Backend)
```bash
railway login
railway init
railway up
```

### Vercel (Frontend)
```bash
vercel --prod
```

### Supabase (Database)
- Create project
- Run migrations
- Connect to backend

## Notes
- Use connection pooling for Supabase (PgBouncer)
- Cache 3D models in R2
- Lazy load 3D viewer
- Compress videos before upload
