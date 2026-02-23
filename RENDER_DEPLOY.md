# DepoSafety V2 - Render.com Deployment

## One-Click Deploy

### Backend (Web Service)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/apoorv0731/Deposafety-v2)

### Frontend (Static Site)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/apoorv0731/Deposafety-v2)

---

## Manual Setup

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Connect your repository

### Step 2: Deploy Backend
1. Click "New +" → "Web Service"
2. Select your GitHub repo
3. Configure:
   - **Name:** deposafety-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** backend
4. Add environment variables (see below)
5. Click "Create Web Service"

### Step 3: Deploy Frontend
1. Click "New +" → "Static Site"
2. Select your GitHub repo
3. Configure:
   - **Name:** deposafety-web
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** dist
   - **Root Directory:** frontend
4. Add environment variable:
   - `VITE_API_URL` = backend URL from Step 2
5. Click "Create Static Site"

---

## Environment Variables

### Backend (Web Service)
```
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///./deposafety.db
SUPABASE_URL=
SUPABASE_KEY=
R2_ENDPOINT_URL=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=deposafety
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
WALLET_PRIVATE_KEY=
CONTRACT_ADDRESS=
SENDGRID_API_KEY=
FROM_EMAIL=noreply@deposafety.com
```

### Frontend (Static Site)
```
VITE_API_URL=https://deposafety-api.onrender.com
```

---

## Free Tier Limits

| Feature | Limit |
|---------|-------|
| Web Services | 1 (always on) |
| Static Sites | Unlimited |
| Bandwidth | 100GB/month |
| Build Minutes | 500/month |
| Disk | 1GB |

---

## URLs After Deploy

- **Backend:** https://deposafety-api.onrender.com
- **Frontend:** https://deposafety-web.onrender.com

---

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure requirements.txt has all dependencies
- Verify Python version (3.11+)

### Environment Variables Not Working
- Redeploy after adding env vars
- Check spelling matches exactly

### CORS Errors
- Update CORS origins in backend/main.py
- Add your frontend URL to allowed origins

---

## Support

- Render Docs: https://render.com/docs
- Status: https://status.render.com
