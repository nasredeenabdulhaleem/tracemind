# TraceMind AI - Security Implementation Guide

## 🔐 Security Overview

This document outlines all security measures implemented in TraceMind AI to ensure a secure, production-ready application.

---

## 🛡️ Authentication & Authorization

### Password Security

**Hashing Algorithm**: bcrypt with 12 rounds
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, hashed_password)
```

**Password Requirements**:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

**Implementation**:
```python
import re

def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

### JWT Token Security

**Configuration**:
```python
SECRET_KEY = os.getenv("SECRET_KEY")  # Min 32 characters
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

**Token Generation**:
```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Token Validation**:
```python
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 🚫 Rate Limiting

### Implementation with slowapi

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@app.post("/auth/login")
@limiter.limit("5/15minutes")
async def login(request: Request, credentials: LoginSchema):
    # Login logic
    pass

@app.post("/auth/register")
@limiter.limit("3/hour")
async def register(request: Request, user: UserCreate):
    # Registration logic
    pass

@app.post("/analysis/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request, analysis: AnalysisRequest):
    # Analysis logic
    pass
```

---

## 🌐 CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)
```

**Production Configuration**:
```env
CORS_ORIGINS=https://tracemind.ai,https://app.tracemind.ai
```

---

## 📁 File Upload Security

### Size Validation

```python
MAX_UPLOAD_SIZE = 104857600  # 100MB

@app.post("/repository/upload")
async def upload_repo(
    file: UploadFile = File(...),
    project_id: str = Form(...)
):
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 100MB limit"
        )
    
    # Process file
    pass
```

### File Type Validation

```python
ALLOWED_EXTENSIONS = {".zip"}

def validate_file_type(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@app.post("/repository/upload")
async def upload_repo(file: UploadFile = File(...)):
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed"
        )
    pass
```

### Virus Scanning (Optional)

```python
import clamd

def scan_file(file_path: str) -> bool:
    cd = clamd.ClamdUnixSocket()
    scan_result = cd.scan(file_path)
    return scan_result[file_path][0] == 'OK'
```

---

## 🔒 Input Validation

### Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, validator, Field
import re

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(None, max_length=1000)
    
    @validator('name')
    def validate_name(cls, v):
        # Prevent XSS
        if '<' in v or '>' in v:
            raise ValueError('Invalid characters in project name')
        return v.strip()
```

### SQL Injection Prevention

**Using SQLAlchemy ORM** (automatically prevents SQL injection):
```python
# SAFE - Parameterized query
user = db.query(User).filter(User.email == email).first()

# SAFE - Using ORM methods
project = db.query(Project).filter(
    Project.id == project_id,
    Project.user_id == user_id
).first()
```

**Never use raw SQL with string formatting**:
```python
# DANGEROUS - Never do this
query = f"SELECT * FROM users WHERE email = '{email}'"

# SAFE - If raw SQL needed, use parameters
query = text("SELECT * FROM users WHERE email = :email")
result = db.execute(query, {"email": email})
```

---

## 🛡️ XSS Protection

### Content Security Policy

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### Output Encoding

```python
import html

def sanitize_output(text: str) -> str:
    return html.escape(text)

# Use in responses
return {
    "message": sanitize_output(user_input)
}
```

---

## 🔐 Environment Variables Security

### .env File Structure

```env
# NEVER commit this file to Git
# Add .env to .gitignore

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tracemind

# JWT
SECRET_KEY=your-super-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Cloudflare R2
R2_ENDPOINT=https://account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_r2_access_key
R2_SECRET_KEY=your_r2_secret_key
R2_BUCKET=tracemind-projects

# watsonx.ai
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Application
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://tracemind.ai
MAX_UPLOAD_SIZE=104857600
```

### Loading Environment Variables

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    r2_endpoint: str
    r2_access_key: str
    r2_secret_key: str
    r2_bucket: str
    
    watsonx_api_key: str
    watsonx_project_id: str
    watsonx_url: str
    
    environment: str = "development"
    debug: bool = False
    cors_origins: str
    max_upload_size: int = 104857600
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

## 🔍 Logging & Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger("tracemind")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Security Event Logging

```python
def log_security_event(event_type: str, user_id: str, details: dict):
    logger.warning(
        f"Security Event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Usage
log_security_event(
    "failed_login_attempt",
    user_id="unknown",
    details={"email": email, "ip": request.client.host}
)
```

---

## 🚨 Error Handling

### Secure Error Messages

```python
from fastapi import HTTPException

# GOOD - Generic error message
raise HTTPException(
    status_code=401,
    detail="Invalid credentials"
)

# BAD - Reveals too much information
raise HTTPException(
    status_code=401,
    detail=f"User {email} not found in database"
)
```

### Global Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return generic error to user
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
```

---

## 🔒 Database Security

### Connection Security

```python
# Use SSL for database connections in production
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
```

### Prepared Statements

```python
# SQLAlchemy automatically uses prepared statements
# This prevents SQL injection
user = db.query(User).filter(User.id == user_id).first()
```

### Row-Level Security

```python
# Ensure users can only access their own data
def get_user_projects(db: Session, user_id: str):
    return db.query(Project).filter(
        Project.user_id == user_id
    ).all()

# Verify ownership before operations
def verify_project_ownership(db: Session, project_id: str, user_id: str):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    return project
```

---

## 🔐 API Security Checklist

- [x] JWT authentication implemented
- [x] Password hashing with bcrypt
- [x] Rate limiting on sensitive endpoints
- [x] CORS properly configured
- [x] Input validation with Pydantic
- [x] SQL injection prevention (ORM)
- [x] XSS protection (CSP headers)
- [x] File upload validation
- [x] Environment variables secured
- [x] HTTPS enforced in production
- [x] Security headers set
- [x] Error messages sanitized
- [x] Logging implemented
- [x] Row-level security
- [x] Token expiration

---

## 🚀 Production Deployment Security

### HTTPS Configuration

```nginx
# Nginx configuration
server {
    listen 443 ssl http2;
    server_name api.tracemind.ai;
    
    ssl_certificate /etc/letsencrypt/live/api.tracemind.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.tracemind.ai/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.tracemind.ai;
    return 301 https://$server_name$request_uri;
}
```

### Docker Security

```dockerfile
# Use non-root user
FROM python:3.11-slim

RUN useradd -m -u 1000 appuser
USER appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📋 Security Audit Checklist

### Pre-Deployment
- [ ] All dependencies updated to latest secure versions
- [ ] No hardcoded secrets in code
- [ ] .env file not committed to Git
- [ ] All API endpoints require authentication (except public ones)
- [ ] Rate limiting configured
- [ ] CORS whitelist configured
- [ ] File upload limits enforced
- [ ] Input validation on all endpoints
- [ ] SQL injection tests passed
- [ ] XSS tests passed
- [ ] CSRF protection implemented
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] Database connections use SSL
- [ ] Logging configured
- [ ] Error messages don't leak sensitive info

### Post-Deployment
- [ ] SSL certificate valid
- [ ] Security headers present
- [ ] Rate limiting working
- [ ] Authentication working
- [ ] File uploads restricted
- [ ] Logs being collected
- [ ] Monitoring alerts configured
- [ ] Backup strategy in place

---

## 🔧 Security Tools

### Dependency Scanning
```bash
# Check for known vulnerabilities
pip install safety
safety check

# Or use pip-audit
pip install pip-audit
pip-audit
```

### Static Analysis
```bash
# Install bandit
pip install bandit

# Run security scan
bandit -r app/
```

### Secrets Detection
```bash
# Install gitleaks
brew install gitleaks

# Scan for secrets
gitleaks detect --source . --verbose
```

---

## 📞 Security Incident Response

### If a Security Issue is Discovered:

1. **Assess Impact**: Determine severity and scope
2. **Contain**: Disable affected functionality if needed
3. **Investigate**: Review logs and identify root cause
4. **Fix**: Implement and test fix
5. **Deploy**: Roll out fix to production
6. **Notify**: Inform affected users if necessary
7. **Document**: Record incident and lessons learned
8. **Review**: Update security measures to prevent recurrence

---

**Last Updated**: 2026-05-01
**Review Frequency**: Quarterly