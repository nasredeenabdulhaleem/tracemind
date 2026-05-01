# TraceMind AI - Technical Implementation Plan

## 🎯 Project Overview

**TraceMind AI** is a Natural Language Bug Intelligence System that uses AI-powered analysis to identify root causes, suggest fixes, and generate regression tests from plain English bug descriptions.

---

## 📋 System Architecture

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

---

## 🗂️ Project Structure

```
tracemind-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/             # API routes
│   │   ├── services/        # Business logic
│   │   ├── agents/          # AI agents
│   │   ├── core/            # Security, exceptions
│   │   └── utils/           # Helpers
│   ├── alembic/             # Migrations
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── context/
│   ├── package.json
│   └── vite.config.js
│
└── docker-compose.yml
```

---

## 🔧 Technology Stack

### Backend
- FastAPI 0.109+, Python 3.11+
- PostgreSQL 15+, SQLAlchemy 2.0+
- JWT Auth: python-jose, passlib[bcrypt]
- Cloud: boto3 (R2), GitPython
- Parsing: tree-sitter
- Vector: faiss-cpu
- AI: ibm-watsonx-ai

### Frontend
- React 18+, Vite 5+
- TailwindCSS 3+
- Axios, React Router v6
- Lucide React (icons)

---

## 📊 Database Schema

### Users
```sql
id UUID PRIMARY KEY
email VARCHAR(255) UNIQUE NOT NULL
username VARCHAR(100) UNIQUE NOT NULL
hashed_password VARCHAR(255) NOT NULL
is_active BOOLEAN DEFAULT TRUE
created_at TIMESTAMP
```

### Projects
```sql
id UUID PRIMARY KEY
user_id UUID REFERENCES users(id)
name VARCHAR(255) NOT NULL
repo_url VARCHAR(500)
repo_type VARCHAR(20) -- 'github' or 'zip'
r2_object_key VARCHAR(500)
is_indexed BOOLEAN DEFAULT FALSE
indexing_status VARCHAR(50)
created_at TIMESTAMP
```

### Code Chunks
```sql
id UUID PRIMARY KEY
project_id UUID REFERENCES projects(id)
file_path VARCHAR(500) NOT NULL
chunk_index INTEGER
content TEXT NOT NULL
start_line INTEGER
end_line INTEGER
language VARCHAR(50)
embedding_id VARCHAR(100)
```

### Analysis History
```sql
id UUID PRIMARY KEY
project_id UUID REFERENCES projects(id)
user_id UUID REFERENCES users(id)
bug_description TEXT NOT NULL
affected_files JSONB
root_cause TEXT
explanation_simple TEXT
explanation_technical TEXT
suggested_fix TEXT
generated_test TEXT
processing_time_ms INTEGER
created_at TIMESTAMP
```

---

## 🚀 Implementation Phases

### Phase 1: Project Foundation
- Initialize Git repo
- Create directory structure
- Setup FastAPI + React
- Configure TailwindCSS
- Docker Compose for PostgreSQL
- Create .env.example files

**Deliverables**: Running FastAPI + React dev servers

---

### Phase 2: Database Setup
- Create SQLAlchemy models
- Setup Alembic migrations
- Define all tables
- Apply initial migration

**Deliverables**: Database schema created

---

### Phase 3: Authentication System
- JWT token generation/validation
- Password hashing (bcrypt)
- Auth API routes: `/auth/register`, `/auth/login`
- Protected route middleware

**Deliverables**: Working auth system

---

### Phase 4: Project Management
- Project CRUD operations
- API routes: POST/GET/DELETE `/projects`
- Project ownership validation

**Deliverables**: Project management working

---

### Phase 5: Cloudflare R2 Integration
- Configure boto3 for R2
- Create RepoStorageService
- Methods: upload_repo, download_repo, delete_temp
- Temp directory management

**Deliverables**: R2 storage operational

---

### Phase 6: Repository Ingestion
- GitHub clone functionality (GitPython)
- ZIP upload handling
- Integration with R2 storage
- API routes: `/repo/connect`, `/repo/upload`

**Flow**: Clone/Upload → Compress → R2 → Delete temp

**Deliverables**: Repo ingestion working

---

### Phase 7: Code Parsing Engine
- Install tree-sitter + language bindings
- Parse Python, JavaScript, TypeScript
- Extract functions/classes
- Chunk code (max 500 lines, 50 line overlap)
- Store in code_chunks table

**Deliverables**: Code parsing functional

---

### Phase 8: Vector Indexing (FAISS)
- Generate embeddings (sentence-transformers or watsonx)
- Create FAISS index
- Implement similarity search
- Persist index to disk
- API: POST `/projects/{id}/index`

**Deliverables**: Vector search working

---

### Phase 9: watsonx.ai Integration
- Configure watsonx credentials
- Create base agent class
- Implement 5 agents:
  1. Bug Understanding Agent
  2. Code Retrieval Agent
  3. Root Cause Agent
  4. Fix Generator Agent
  5. Test Generator Agent

**Deliverables**: All agents functional

---

### Phase 10: Bug Analysis Pipeline
- Orchestrate agent flow
- API: POST `/analysis/analyze`
- Store results in analysis_history
- Error handling + retries

**Flow**: Input → Understanding → Retrieval → Root Cause → Fix → Test → Output

**Deliverables**: End-to-end analysis working

---

### Phase 11: Frontend Foundation
- Setup React + Vite + Tailwind
- Create component structure
- Setup routing
- Create API service layer
- AuthContext for state management

**Deliverables**: React app structure ready

---

### Phase 12: Auth Pages
- Login page + form
- Signup page + form
- Form validation
- Token storage (localStorage)
- Protected routes

**Deliverables**: Auth UI working

---

### Phase 13: Dashboard & Projects
- Dashboard page
- ProjectCard, ProjectList components
- CreateProjectModal
- Repository connection UI
- ZIP upload UI

**Deliverables**: Project management UI complete

---

### Phase 14: Bug Analysis Interface
- AnalysisView page
- BugInputForm component
- AnalysisResult component
- CodeViewer with syntax highlighting
- Copy-to-clipboard functionality

**Deliverables**: Analysis UI complete

---

### Phase 15: API Integration
- Configure Axios interceptors
- Implement token refresh
- Add error handling
- Connect all frontend to backend

**Deliverables**: Full integration working

---

### Phase 16: Security Hardening
- Input sanitization
- CORS configuration
- Rate limiting
- File upload validation
- Security headers
- Dependency audit

**Deliverables**: Security measures in place

---

### Phase 17: Error Handling & Logging
- Custom exception classes
- Global exception handler
- Structured logging
- Error boundaries (React)

**Deliverables**: Robust error handling

---

### Phase 18: Testing
- Unit tests (pytest)
- Integration tests
- Frontend tests (Vitest)
- Test critical paths
- Target: >70% coverage

**Deliverables**: Test suite complete

---

### Phase 19: Performance Optimization
- Database query optimization
- FAISS search optimization
- Code splitting (frontend)
- Lazy loading
- Bundle size reduction

**Targets**: Page load <2s, Analysis <10s

---

### Phase 20: Documentation & Demo
- README.md
- API documentation
- Setup instructions
- Demo script
- Sample repository
- Architecture docs

**Deliverables**: Demo-ready application

---

## 🤖 AI Agent System

### Agent Flow
```
Bug Input
  ↓
Understanding Agent (extract intent)
  ↓
Retrieval Agent (find relevant code via FAISS)
  ↓
Root Cause Agent (analyze issue)
  ↓
Fix Generator Agent (create patch)
  ↓
Test Generator Agent (create test)
  ↓
Aggregated Result
```

### Agent Details

**1. Bug Understanding Agent**
- Model: granite-13b-chat-v2
- Input: Raw bug description
- Output: Structured intent, suspected modules

**2. Code Retrieval Agent**
- Uses: FAISS similarity search
- Input: Bug intent + project_id
- Output: Top 5 relevant code chunks

**3. Root Cause Agent**
- Model: granite-13b-chat-v2
- Input: Bug intent + retrieved code
- Output: Root cause analysis + reasoning

**4. Fix Generator Agent**
- Model: granite-20b-code-instruct
- Input: Root cause + affected code
- Output: Code patch + explanation

**5. Test Generator Agent**
- Model: granite-20b-code-instruct
- Input: Bug + fix
- Output: Regression test code

---

## 🔐 Security Measures

- Password hashing: bcrypt (12 rounds)
- JWT tokens: HS256, 24h expiry
- Rate limiting: 5 attempts/15min for auth
- CORS: Whitelist frontend origin
- Input validation: Pydantic schemas
- File upload: 100MB limit, type validation
- SQL injection: SQLAlchemy ORM
- XSS protection: CSP headers
- HTTPS only in production
- Environment variables for secrets

---

## ⚙️ Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/tracemind
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

R2_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=tracemind-projects

WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
MAX_UPLOAD_SIZE=104857600
TEMP_DIR=/tmp/tracemind
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=TraceMind AI
```

---

## 📦 Key Dependencies

### Backend
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
boto3==1.34.34
GitPython==3.1.41
tree-sitter==0.20.4
faiss-cpu==1.7.4
sentence-transformers==2.3.1
ibm-watsonx-ai==0.2.0
pydantic==2.5.0
python-dotenv==1.0.0
```

### Frontend
```json
{
  "react": "^18.2.0",
  "react-router-dom": "^6.21.0",
  "axios": "^1.6.0",
  "lucide-react": "^0.300.0"
}
```

---

## 🎯 Success Criteria

### Performance
- Page load: <2 seconds
- Bug analysis: <10 seconds
- Repository indexing: <2 minutes (1000 files)
- API response: <500ms

### Quality
- Test coverage: >70%
- No critical security vulnerabilities
- No critical linting errors
- Clean, documented code

### Demo Requirements
- User can register and login
- User can create project
- User can connect GitHub repo or upload ZIP
- System indexes codebase
- User can submit bug description
- System returns: root cause, fix, test
- UI is clean and intuitive
- Demo completes in <5 minutes

---

## 🚨 Critical Notes

### R2 Storage Flow
1. GitHub: Clone → Compress → Upload to R2 → Delete local
2. ZIP: Upload to R2 → Delete local
3. Indexing: Download from R2 → Extract to /tmp → Parse → Index → Delete temp

### Stateless Backend
- Never persist repos on backend disk
- Always use /tmp for processing
- Always cleanup after indexing
- R2 is source of truth for repos

### Security First
- All inputs validated
- All secrets in environment variables
- Rate limiting on auth endpoints
- File upload size limits enforced
- CORS properly configured

---

## 📝 Next Steps

1. Review this plan with stakeholders
2. Confirm watsonx.ai credentials available
3. Setup Cloudflare R2 bucket
4. Setup PostgreSQL database
5. Begin Phase 1 implementation

---

**Plan Status**: Ready for Review
**Estimated Timeline**: 4-6 weeks (full-time)
**Team Size**: 1-2 developers
**Complexity**: High (AI integration, multi-service architecture)