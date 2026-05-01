# 🧠 TraceMind AI

**Natural Language Bug Intelligence System**

TraceMind AI is an AI-powered debugging assistant that analyzes codebases and identifies root causes, suggests fixes, and generates regression tests from plain English bug descriptions.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)

---

## 🎯 Features

- **🔐 Secure Authentication**: JWT-based auth with bcrypt password hashing
- **📁 Project Management**: Create and manage multiple code projects
- **📦 Repository Integration**: Connect GitHub repos or upload ZIP files
- **🧠 AI-Powered Analysis**: 5-agent system using IBM watsonx.ai
- **🔍 Semantic Code Search**: FAISS vector database for intelligent code retrieval
- **☁️ Cloud Storage**: Cloudflare R2 for scalable, stateless architecture
- **🎨 Clean UI**: React + TailwindCSS for intuitive user experience
- **🔒 Production-Ready Security**: Rate limiting, input validation, CORS, and more

---

## 🏗️ Architecture

```
Frontend (React + Vite + Tailwind)
         ↓ REST API
Backend (FastAPI + Python 3.11+)
         ↓
┌────────┼────────┬──────────┐
│        │        │          │
PostgreSQL  R2   watsonx   FAISS
Database  Storage  .ai    VectorDB
```

### AI Agent System

```
Bug Input → Understanding Agent → Retrieval Agent → Root Cause Agent
                                                            ↓
                                                    Fix Generator Agent
                                                            ↓
                                                    Test Generator Agent
                                                            ↓
                                                    Aggregated Result
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- Cloudflare R2 account
- IBM watsonx.ai credentials

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/tracemind-ai.git
cd tracemind-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your credentials

# Start PostgreSQL (using Docker)
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Edit .env with backend URL

# Start frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 📦 Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🔧 Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tracemind

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Cloudflare R2
R2_ENDPOINT=https://account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=tracemind-projects

# watsonx.ai
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Application
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
MAX_UPLOAD_SIZE=104857600
```

### Frontend Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=TraceMind AI
```

---

## 📚 Documentation

- **[Technical Plan](TECHNICAL_PLAN.md)**: Complete implementation guide with 20 phases
- **[API Specification](API_SPECIFICATION.md)**: Detailed API endpoint documentation
- **[Security Guide](SECURITY_GUIDE.md)**: Security implementation and best practices
- **[Deployment & Demo Guide](DEPLOYMENT_DEMO_GUIDE.md)**: Production deployment and demo preparation

---

## 🎬 Demo Flow

1. **Register/Login**: Create account or sign in
2. **Create Project**: Name your project
3. **Connect Repository**: GitHub URL or ZIP upload
4. **Index Codebase**: System parses and indexes code (1-2 minutes)
5. **Submit Bug**: Describe bug in plain English
6. **Get Results**: Receive root cause, fix, and test in <10 seconds

### Example Bug Description

```
"Checkout breaks after applying discount code. Users see 500 error."
```

### Example Output

**Affected Files**: `checkout.js`, `discount.js`

**Root Cause**: Null pointer exception when discount validation fails

**Fix**: Add null check before accessing discount properties

**Test**: Regression test for invalid discount codes

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

---

## 🔐 Security Features

- ✅ JWT authentication with 24h expiry
- ✅ Bcrypt password hashing (12 rounds)
- ✅ Rate limiting (5 login attempts/15min)
- ✅ CORS whitelist configuration
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS protection (CSP headers)
- ✅ File upload validation (100MB limit)
- ✅ Environment variable security
- ✅ HTTPS enforcement in production

---

## 📊 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Page Load | < 2 seconds | ✅ |
| Bug Analysis | < 10 seconds | ✅ |
| Repository Indexing | < 2 min (1000 files) | ✅ |
| API Response | < 500ms | ✅ |

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0+
- **Authentication**: python-jose, passlib[bcrypt]
- **Cloud Storage**: boto3 (Cloudflare R2)
- **Code Parsing**: tree-sitter
- **Vector Search**: faiss-cpu
- **AI**: ibm-watsonx-ai

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite 5+
- **Styling**: TailwindCSS 3+
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Icons**: Lucide React

---

## 📁 Project Structure

```
tracemind-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/                 # API routes
│   │   ├── services/            # Business logic
│   │   ├── agents/              # AI agents
│   │   └── core/                # Security, config
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   └── hooks/               # Custom hooks
│   └── package.json
│
├── TECHNICAL_PLAN.md            # Implementation guide
├── API_SPECIFICATION.md         # API documentation
├── SECURITY_GUIDE.md            # Security practices
├── DEPLOYMENT_DEMO_GUIDE.md     # Deployment guide
└── docker-compose.yml
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project
- `DELETE /api/v1/projects/{id}` - Delete project

### Repository
- `POST /api/v1/repository/connect` - Connect GitHub repo
- `POST /api/v1/repository/upload` - Upload ZIP file

### Analysis
- `POST /api/v1/analysis/analyze` - Analyze bug
- `GET /api/v1/analysis/history` - Get analysis history

See [API_SPECIFICATION.md](API_SPECIFICATION.md) for complete documentation.

---

## 🎯 Roadmap

### Phase 1: Foundation ✅
- [x] Project setup
- [x] Database schema
- [x] Authentication system

### Phase 2: Core Features ✅
- [x] Project management
- [x] Repository ingestion
- [x] Code parsing & indexing

### Phase 3: AI Integration ✅
- [x] watsonx.ai integration
- [x] Agent system
- [x] Bug analysis pipeline

### Phase 4: Frontend ✅
- [x] React application
- [x] Authentication UI
- [x] Dashboard & project management
- [x] Bug analysis interface

### Phase 5: Production Ready 🚧
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Testing & QA
- [ ] Documentation

### Future Enhancements 📋
- [ ] Multi-language support
- [ ] Real-time collaboration
- [ ] GitHub integration (webhooks)
- [ ] Advanced analytics
- [ ] Custom AI model training

---

## 🐛 Known Issues

- Analysis may timeout for very large codebases (>10,000 files)
- GitHub private repos require personal access token
- watsonx.ai rate limits may affect concurrent users

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IBM watsonx.ai** for AI capabilities
- **Cloudflare R2** for scalable storage
- **FastAPI** for excellent Python framework
- **React** for powerful UI library

---

## 📞 Support

- **Documentation**: See docs folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/tracemind-ai/issues)
- **Email**: support@tracemind.ai

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ for developers who hate debugging**

---

## 🚀 Getting Started Checklist

- [ ] Clone repository
- [ ] Setup PostgreSQL database
- [ ] Configure environment variables
- [ ] Install backend dependencies
- [ ] Run database migrations
- [ ] Install frontend dependencies
- [ ] Start backend server
- [ ] Start frontend server
- [ ] Create test account
- [ ] Create test project
- [ ] Upload sample repository
- [ ] Run first bug analysis
- [ ] Review results

**Ready to eliminate debugging headaches? Let's get started!** 🎉