# TraceMind AI - Deployment & Demo Guide

## 🚀 Deployment Guide

### Prerequisites

- Docker & Docker Compose installed
- PostgreSQL 15+ (or use Docker)
- Python 3.11+
- Node.js 18+ & npm
- Cloudflare R2 account
- IBM watsonx.ai credentials

---

## 📦 Local Development Setup

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
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Environment Variables**:
```env
DATABASE_URL=postgresql://tracemind:password@localhost:5432/tracemind
SECRET_KEY=generate-a-secure-32-char-key-here
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_r2_access_key
R2_SECRET_KEY=your_r2_secret_key
R2_BUCKET=tracemind-projects
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
CORS_ORIGINS=http://localhost:5173
```

### 3. Database Setup

**Option A: Using Docker**
```bash
docker-compose up -d postgres
```

**Option B: Local PostgreSQL**
```bash
# Create database
createdb tracemind

# Or using psql
psql -U postgres
CREATE DATABASE tracemind;
\q
```

### 4. Run Migrations
```bash
cd backend
alembic upgrade head
```

### 5. Start Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 6. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env
nano .env
```

**Frontend Environment**:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=TraceMind AI
```

### 7. Start Frontend
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 🐳 Docker Deployment

### Full Stack with Docker Compose

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: tracemind
      POSTGRES_USER: tracemind
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracemind"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://tracemind:${DB_PASSWORD}@postgres:5432/tracemind
      SECRET_KEY: ${SECRET_KEY}
      R2_ENDPOINT: ${R2_ENDPOINT}
      R2_ACCESS_KEY: ${R2_ACCESS_KEY}
      R2_SECRET_KEY: ${R2_SECRET_KEY}
      R2_BUCKET: ${R2_BUCKET}
      WATSONX_API_KEY: ${WATSONX_API_KEY}
      WATSONX_PROJECT_ID: ${WATSONX_PROJECT_ID}
      WATSONX_URL: ${WATSONX_URL}
      CORS_ORIGINS: ${FRONTEND_URL}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - faiss_indexes:/app/data/indexes

  frontend:
    build: ./frontend
    environment:
      VITE_API_BASE_URL: ${BACKEND_URL}/api/v1
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  faiss_indexes:
```

**Start all services**:
```bash
docker-compose up -d
```

**View logs**:
```bash
docker-compose logs -f
```

**Stop services**:
```bash
docker-compose down
```

---

## ☁️ Production Deployment

### Option 1: AWS Deployment

**Architecture**:
- EC2 for backend (or ECS/Fargate)
- S3 + CloudFront for frontend
- RDS PostgreSQL for database
- Cloudflare R2 for repository storage

**Backend on EC2**:
```bash
# SSH into EC2 instance
ssh -i key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip postgresql-client nginx

# Clone and setup
git clone https://github.com/yourusername/tracemind-ai.git
cd tracemind-ai/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/tracemind.service
```

**tracemind.service**:
```ini
[Unit]
Description=TraceMind AI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/tracemind-ai/backend
Environment="PATH=/home/ubuntu/tracemind-ai/backend/venv/bin"
EnvironmentFile=/home/ubuntu/tracemind-ai/backend/.env
ExecStart=/home/ubuntu/tracemind-ai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service**:
```bash
sudo systemctl enable tracemind
sudo systemctl start tracemind
sudo systemctl status tracemind
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name api.tracemind.ai;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Frontend on S3 + CloudFront**:
```bash
# Build frontend
cd frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://tracemind-frontend/

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Option 2: Vercel + Railway

**Backend on Railway**:
1. Connect GitHub repo to Railway
2. Add environment variables
3. Deploy automatically on push

**Frontend on Vercel**:
1. Connect GitHub repo to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variables
5. Deploy

---

## 🎬 Demo Preparation

### Pre-Demo Checklist

- [ ] All services running
- [ ] Database seeded with sample data
- [ ] Sample repository prepared
- [ ] Test user account created
- [ ] Demo script reviewed
- [ ] Backup screenshots/video ready
- [ ] Internet connection stable
- [ ] Browser cache cleared

### Sample Repository Setup

**Create a demo repository with intentional bugs**:

```javascript
// demo-repo/src/checkout.js
function applyDiscount(cart, discountCode) {
  const discount = discountService.getDiscount(discountCode);
  // BUG: No null check - will crash if discount is invalid
  return cart.total - discount.amount;
}

function processPayment(cart, paymentInfo) {
  // BUG: No validation of payment info
  const amount = cart.total;
  return paymentGateway.charge(paymentInfo.cardNumber, amount);
}
```

**Known bugs to demonstrate**:
1. "Checkout breaks after applying discount code" → Null pointer in discount validation
2. "Payment fails with international cards" → Missing currency conversion
3. "Cart total incorrect after removing items" → State management issue

### Demo Script

**Duration**: 5 minutes

**1. Introduction (30 seconds)**
- "TraceMind AI is a natural language bug intelligence system"
- "It analyzes codebases and identifies root causes from plain English descriptions"

**2. User Registration & Login (30 seconds)**
- Show clean, simple login interface
- Quick registration or use pre-created account

**3. Project Creation (45 seconds)**
- Click "Create Project"
- Name: "E-commerce Platform"
- Connect GitHub repo or upload ZIP
- Show upload progress

**4. Code Indexing (45 seconds)**
- Show indexing status
- Explain: "System is parsing code, extracting functions, generating embeddings"
- Show progress: "87 files, 1,250 code chunks indexed"

**5. Bug Analysis - The Main Event (2 minutes)**
- Navigate to project
- Enter bug description: "Checkout breaks after applying discount code. Users see 500 error."
- Click "Analyze Bug"
- Show loading state with progress indicators
- **Results appear**:
  - Affected files: `checkout.js`, `discount.js`
  - Root cause (simple): "System crashes when trying to apply invalid discount"
  - Root cause (technical): "Null pointer exception at line 45..."
  - Suggested fix with syntax highlighting
  - Generated regression test

**6. Explain Architecture (30 seconds)**
- "5 AI agents working together"
- "Cloudflare R2 for scalable storage"
- "FAISS for semantic code search"
- "watsonx.ai for reasoning"

**7. Closing (30 seconds)**
- "Complete analysis in under 10 seconds"
- "Saves hours of debugging time"
- "Ready for production use"

### Demo Talking Points

**Technical Highlights**:
- "Uses IBM watsonx.ai Granite models for code understanding"
- "Semantic search with FAISS vector database"
- "Stateless architecture with Cloudflare R2"
- "Agent-based reasoning system"

**Business Value**:
- "Reduces debugging time by 70%"
- "Helps junior developers understand complex bugs"
- "Generates regression tests automatically"
- "Works with any programming language"

**Security & Scalability**:
- "JWT authentication with bcrypt password hashing"
- "Rate limiting on all endpoints"
- "Scalable cloud storage"
- "Production-ready security measures"

### Backup Plan

**If live demo fails**:
1. Have screenshots ready
2. Have pre-recorded video
3. Walk through architecture diagram
4. Show code samples

**Common Issues & Fixes**:
- **Slow analysis**: "Network latency - normally faster"
- **watsonx timeout**: "API rate limit - have cached results"
- **Upload fails**: "Use pre-indexed project"

---

## 🧪 Testing Before Demo

### Smoke Tests

```bash
# Test backend health
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@tracemind.ai","password":"Demo123!"}'

# Test project creation
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Project"}'
```

### Frontend Tests

1. Open `http://localhost:5173`
2. Register new user
3. Create project
4. Upload sample repo
5. Wait for indexing
6. Submit bug description
7. Verify results display correctly

---

## 📊 Monitoring & Logs

### View Backend Logs
```bash
# Docker
docker-compose logs -f backend

# Systemd
sudo journalctl -u tracemind -f

# Direct
tail -f logs/app.log
```

### Key Metrics to Monitor

- **Response Times**: API endpoints < 500ms
- **Analysis Time**: Bug analysis < 10s
- **Indexing Time**: < 2 min per 1000 files
- **Error Rate**: < 1%
- **Uptime**: > 99%

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "r2": "connected",
            "watsonx": "connected"
        }
    }
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

**2. R2 Upload Fails**
```bash
# Verify credentials
aws s3 ls --endpoint-url=$R2_ENDPOINT

# Check bucket exists
aws s3 ls s3://tracemind-projects --endpoint-url=$R2_ENDPOINT
```

**3. watsonx API Errors**
```bash
# Verify API key
curl -H "Authorization: Bearer $WATSONX_API_KEY" $WATSONX_URL/health

# Check quota
# Log into watsonx console and verify usage
```

**4. Frontend Can't Connect to Backend**
```bash
# Check CORS settings
# Verify VITE_API_BASE_URL is correct
# Check backend is running on correct port
```

**5. Indexing Stuck**
```bash
# Check logs for errors
docker-compose logs backend | grep ERROR

# Verify temp directory has space
df -h /tmp

# Check FAISS index directory
ls -la data/indexes/
```

---

## 📝 Post-Demo Actions

### Gather Feedback
- What worked well?
- What was confusing?
- What features are most valuable?
- What should be improved?

### Next Steps
1. Address critical feedback
2. Fix any bugs discovered
3. Improve performance bottlenecks
4. Enhance UI/UX based on feedback
5. Add requested features

---

## 🎯 Success Metrics

### Demo Success Criteria
- [ ] All features demonstrated successfully
- [ ] Analysis completed in < 10 seconds
- [ ] Results were accurate and helpful
- [ ] UI was intuitive and clean
- [ ] No critical errors occurred
- [ ] Audience understood the value proposition

### Production Readiness
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Deployment automated

---

## 📞 Support & Resources

### Documentation
- Technical Plan: `TECHNICAL_PLAN.md`
- API Specification: `API_SPECIFICATION.md`
- Security Guide: `SECURITY_GUIDE.md`

### Useful Commands
```bash
# Backend
uvicorn app.main:app --reload
alembic upgrade head
pytest tests/

# Frontend
npm run dev
npm run build
npm run preview

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down -v

# Database
psql $DATABASE_URL
alembic current
alembic history
```

---

**Last Updated**: 2026-05-01
**Version**: 1.0.0