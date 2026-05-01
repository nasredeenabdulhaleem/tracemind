# 🧠 TraceMind AI - Intelligent Bug Analysis Platform

AI-powered bug analysis tool that uses IBM watsonx.ai to understand, locate, and fix bugs in your codebase automatically.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

## 🚀 Features

- **🤖 AI-Powered Analysis**: 5 specialized agents for comprehensive bug analysis
- **🔍 Smart Code Search**: Vector-based semantic code search with FAISS
- **💡 Root Cause Detection**: Deep analysis to find the true source of bugs
- **🛠️ Fix Generation**: Automatic code fix suggestions with best practices
- **✅ Test Generation**: Auto-generated test cases to verify fixes
- **📦 Multi-Language Support**: Python, JavaScript, TypeScript, and more
- **☁️ Cloud Storage**: Cloudflare R2 for scalable repository storage
- **🎨 Modern UI**: Clean React interface with TailwindCSS

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React UI  │────▶│  FastAPI     │────▶│ watsonx.ai  │
│  (Frontend) │     │  (Backend)   │     │  (5 Agents) │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────▼────┐  ┌────▼─────┐
              │PostgreSQL│  │Cloudflare│
              │          │  │    R2    │
              └──────────┘  └──────────┘
```

### AI Agents Pipeline

1. **Bug Understanding Agent** - Analyzes bug description
2. **Code Retrieval Agent** - Finds relevant code using vector search
3. **Root Cause Agent** - Identifies the underlying issue
4. **Fix Generator Agent** - Creates code fixes
5. **Test Generator Agent** - Generates validation tests

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- IBM watsonx.ai account
- Cloudflare R2 account

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd trace-mind
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with API URL
npm run dev
```

### 4. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🐳 Docker Deployment

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed installation instructions
- [User Guide](USER_GUIDE.md) - How to use the platform
- [API Specification](API_SPECIFICATION.md) - API endpoints documentation
- [Security Guide](SECURITY_GUIDE.md) - Security best practices
- [Deployment Guide](DEPLOYMENT_DEMO_GUIDE.md) - Production deployment

## 🎯 Usage Example

1. **Create Project**: Upload your codebase (ZIP or GitHub)
2. **Parse Code**: Extract functions and classes
3. **Index**: Build vector embeddings for search
4. **Analyze Bug**: Describe the issue in natural language
5. **Get Results**: Root cause, fix, and tests in seconds

### Example Bug Description
```
"User authentication fails after password reset with 401 error.
The reset email is received but login still shows invalid credentials."
```

### AI Response
- **Root Cause**: Session token not invalidated after password change
- **Fix**: Add token invalidation in password reset endpoint
- **Test**: Automated test to verify token refresh

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database operations
- Alembic - Database migrations
- watsonx.ai - IBM's AI models
- FAISS - Vector similarity search
- tree-sitter - Code parsing

**Frontend:**
- React 18 - UI library
- Vite - Build tool
- TailwindCSS - Styling
- React Router - Navigation
- Axios - HTTP client

**Infrastructure:**
- PostgreSQL - Primary database
- Cloudflare R2 - Object storage
- Docker - Containerization
- Nginx - Web server

## 📊 Project Structure

```
trace-mind/
├── backend/
│   ├── app/
│   │   ├── agents/        # AI agents
│   │   ├── api/           # API routes
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   └── App.jsx
│   └── package.json
└── docker-compose.yml
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- IBM watsonx.ai for AI models
- Cloudflare for R2 storage
- Open source community

## 📞 Support

- Documentation: [docs](/)
- Issues: [GitHub Issues](repository-url/issues)
- Email: support@tracemind.ai

---

Built with ❤️ for developers by developers