# TraceMind AI - Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+ (optional)
- Git

## Backend Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd trace-mind
```

### 2. Backend Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/tracemind
SECRET_KEY=your-secret-key-here
WATSONX_API_KEY=your-watsonx-api-key
WATSONX_PROJECT_ID=your-project-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=tracemind-projects
R2_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com
```

### 4. Database Setup
```bash
# Start PostgreSQL (Docker)
docker-compose up -d postgres

# Run migrations
alembic upgrade head
```

### 5. Start Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: http://localhost:8000

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Start Frontend
```bash
npm run dev
```

Frontend runs at: http://localhost:5173

## watsonx.ai Setup

### 1. Get API Key
1. Go to IBM Cloud: https://cloud.ibm.com
2. Create watsonx.ai instance
3. Generate API key
4. Create project and get project ID

### 2. Configure Models
The app uses:
- `ibm/granite-13b-chat-v2` - Bug understanding & root cause
- `ibm/granite-20b-code-instruct` - Fix generation & tests

## Cloudflare R2 Setup

### 1. Create Bucket
1. Go to Cloudflare Dashboard
2. Navigate to R2
3. Create bucket: `tracemind-projects`

### 2. Generate Access Keys
1. Go to R2 settings
2. Create API token
3. Copy Access Key ID and Secret Access Key

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Production Deployment

See [DEPLOYMENT_DEMO_GUIDE.md](DEPLOYMENT_DEMO_GUIDE.md) for production setup.

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### watsonx.ai API Errors
- Verify API key is valid
- Check project ID
- Ensure sufficient credits

### R2 Upload Failures
- Verify bucket exists
- Check access keys
- Ensure CORS is configured

## Support

For issues, check:
- [GitHub Issues](repository-url/issues)
- [Documentation](README.md)
- [API Specification](API_SPECIFICATION.md)