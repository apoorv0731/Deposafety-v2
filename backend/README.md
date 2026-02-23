# DepoSafety V2 - Backend

A production-ready FastAPI backend for the DepoSafety property inspection platform.

## Features

- **FastAPI** - Modern, fast web framework
- **Supabase PostgreSQL** - Database and authentication
- **Cloudflare R2** - S3-compatible video storage
- **Polygon Mumbai** - Blockchain anchoring for inspection proofs
- **SendGrid** - Email notifications
- **Webhook Support** - 3D processing completion callbacks

## Project Structure

```
backend/
├── main.py              # FastAPI application with all endpoints
├── models.py            # Pydantic models for request/response
├── database.py          # Supabase client configuration
├── storage.py           # Cloudflare R2 S3 client
├── blockchain.py        # Polygon blockchain anchoring
├── email_service.py     # SendGrid email integration
├── config.py            # Environment configuration
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

3. Run the development server:
```bash
uvicorn main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase service role key |
| `R2_ENDPOINT_URL` | Cloudflare R2 endpoint |
| `R2_ACCESS_KEY_ID` | R2 access key |
| `R2_SECRET_ACCESS_KEY` | R2 secret key |
| `R2_BUCKET_NAME` | R2 bucket for videos |
| `POLYGON_RPC_URL` | Polygon Mumbai RPC endpoint |
| `WALLET_PRIVATE_KEY` | Wallet for blockchain transactions |
| `CONTRACT_ADDRESS` | DepoSafety smart contract address |
| `SENDGRID_API_KEY` | SendGrid API key |
| `FROM_EMAIL` | Sender email address |
