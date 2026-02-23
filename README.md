# DepoSafety V2

**Forensic-Grade 3D Evidence for Security Deposit Protection**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react)](https://reactjs.org)

## 🎯 Problem

Tenants lose $45B annually in security deposit disputes. Standard photos fail in court because they lack:
- Scale and measurements
- Tamper-proof timestamps
- Verifiable authenticity

## 💡 Solution

DepoSafety creates **forensic-grade 3D scans** with:
- 📸 3D Gaussian Splatting (millimeter accuracy)
- 🔐 SHA-256 hashing (tamper detection)
- ⛓️ Blockchain anchoring (court-admissible proof)
- 📱 Web-based (no app install)

## ✨ Features

### Core
- ✅ User authentication (JWT + Supabase)
- ✅ Property profile management
- ✅ Video capture with AR guidance
- ✅ On-device SHA-256 hashing
- ✅ 3D model generation
- ✅ Evidence reports with certificates
- ✅ Public verification portal

### Advanced
- 🎨 3D interactive viewer (Three.js)
- ⛓️ Polygon blockchain anchoring
- 📧 Email notifications (SendGrid)
- 📄 PDF report generation
- 📱 PWA (install on home screen)
- 🔄 Offline mode support

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│  Supabase   │
│   (Vercel)  │     │  (Railway)  │     │  (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│ Cloudflare  │     │    ML       │
│    R2       │     │  Pipeline   │
│(Video/3D)   │     │(Colab/Local)│
└─────────────┘     └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  Polygon    │
                     │ Blockchain  │
                     └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Free accounts: Railway, Supabase, Vercel, Cloudflare

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Start dev server
npm run dev
```

### Docker (Production)

```bash
docker-compose up -d
```

## 📁 Project Structure

```
deposafety-v2/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config, security
│   │   ├── models/      # Database models
│   │   └── services/    # Business logic
│   ├── tests/
│   └── Dockerfile
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Route pages
│   │   ├── hooks/       # Custom hooks
│   │   └── services/    # API client
│   ├── tests/
│   └── Dockerfile
├── ml-pipeline/          # 3DGS processing
│   ├── colab_3dgs.ipynb
│   └── local_3dgs.py
├── blockchain/           # Smart contracts
│   ├── EvidenceAnchor.sol
│   └── deploy.py
├── infrastructure/       # Deployment configs
│   ├── railway.json
│   ├── vercel.json
│   └── docker-compose.yml
└── docs/                 # Documentation
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov

# Frontend tests
cd frontend
npm test --coverage

# E2E tests
pytest tests/e2e/

# Load tests
locust -f tests/load/
```

## 📦 Deployment

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
1. Create project at supabase.com
2. Run migrations: `supabase db push`
3. Get API keys for .env

## 🎨 Design

See [docs/design/](docs/design/) for:
- Design system
- Wireframes
- Mockups

## 📖 Documentation

- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

## 🔒 Security

- JWT authentication with refresh tokens
- SHA-256 hashing for evidence integrity
- Row Level Security in PostgreSQL
- CORS protection
- Rate limiting
- Input sanitization (XSS/SQL injection prevention)

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing`
5. Open Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📞 Support

- Discord: [Join our community]()
- Email: support@deposafety.com
- Issues: [GitHub Issues]()

## 🙏 Acknowledgments

- 3D Gaussian Splatting: [Original Paper](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/)
- Three.js: [3D Library](https://threejs.org)
- FastAPI: [Web Framework](https://fastapi.tiangolo.com)
- Supabase: [Backend Platform](https://supabase.com)

---

**Built with ❤️ for tenants everywhere**
