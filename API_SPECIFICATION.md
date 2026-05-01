# TraceMind AI - API Specification

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.tracemind.ai/api/v1
```

---

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

---

## 🔐 Authentication Endpoints

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!"
}

Response 201:
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2026-05-01T15:30:00Z"
}

Response 400:
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email already registered"
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe"
  }
}

Response 401:
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>

Response 200:
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2026-05-01T15:30:00Z"
}
```

---

## 📁 Project Endpoints

### Create Project
```http
POST /projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Web App",
  "description": "E-commerce platform"
}

Response 201:
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "My Web App",
  "description": "E-commerce platform",
  "is_indexed": false,
  "indexing_status": "pending",
  "created_at": "2026-05-01T15:30:00Z"
}
```

### List Projects
```http
GET /projects?page=1&limit=10
Authorization: Bearer <token>

Response 200:
{
  "projects": [
    {
      "id": "uuid",
      "name": "My Web App",
      "description": "E-commerce platform",
      "repo_url": "https://github.com/user/repo",
      "repo_type": "github",
      "is_indexed": true,
      "indexing_status": "completed",
      "created_at": "2026-05-01T15:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

### Get Project
```http
GET /projects/{project_id}
Authorization: Bearer <token>

Response 200:
{
  "id": "uuid",
  "name": "My Web App",
  "description": "E-commerce platform",
  "repo_url": "https://github.com/user/repo",
  "repo_type": "github",
  "r2_object_key": "projects/user_id/project_id/repo.zip",
  "is_indexed": true,
  "indexing_status": "completed",
  "created_at": "2026-05-01T15:30:00Z",
  "updated_at": "2026-05-01T16:00:00Z"
}
```

### Update Project
```http
PUT /projects/{project_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}

Response 200:
{
  "id": "uuid",
  "name": "Updated Name",
  "description": "Updated description",
  ...
}
```

### Delete Project
```http
DELETE /projects/{project_id}
Authorization: Bearer <token>

Response 200:
{
  "message": "Project deleted successfully"
}
```

---

## 📦 Repository Endpoints

### Connect GitHub Repository
```http
POST /repository/connect
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": "uuid",
  "repo_url": "https://github.com/user/repo"
}

Response 200:
{
  "message": "Repository connected successfully",
  "r2_object_key": "projects/user_id/project_id/repo.zip",
  "status": "uploaded"
}

Response 400:
{
  "error": {
    "code": "INVALID_REPO_URL",
    "message": "Invalid GitHub repository URL"
  }
}
```

### Upload ZIP Repository
```http
POST /repository/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- file: <zip file>
- project_id: uuid

Response 200:
{
  "message": "Repository uploaded successfully",
  "r2_object_key": "projects/user_id/project_id/repo.zip",
  "file_size": 1048576,
  "status": "uploaded"
}

Response 413:
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds 100MB limit"
  }
}
```

---

## 🧠 Indexing Endpoints

### Index Project
```http
POST /projects/{project_id}/index
Authorization: Bearer <token>

Response 202:
{
  "message": "Indexing started",
  "project_id": "uuid",
  "status": "processing"
}

Response 200 (when complete):
{
  "message": "Indexing completed",
  "project_id": "uuid",
  "chunks_indexed": 1250,
  "files_processed": 87,
  "time_taken_ms": 45000,
  "status": "completed"
}
```

### Get Indexing Status
```http
GET /projects/{project_id}/index/status
Authorization: Bearer <token>

Response 200:
{
  "project_id": "uuid",
  "status": "processing",
  "progress": 65,
  "chunks_indexed": 812,
  "files_processed": 56,
  "total_files": 87,
  "started_at": "2026-05-01T15:30:00Z"
}
```

---

## 🐞 Analysis Endpoints

### Analyze Bug
```http
POST /analysis/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": "uuid",
  "bug_description": "Checkout breaks after applying discount code. Users see 500 error."
}

Response 200:
{
  "analysis_id": "uuid",
  "project_id": "uuid",
  "files": [
    "src/services/checkout.js",
    "src/services/discount.js"
  ],
  "root_cause": "The discount validation logic does not handle null values when the discount code is expired or invalid, causing a null pointer exception during checkout.",
  "explanation_simple": "The system crashes when trying to apply an invalid discount code because it doesn't check if the discount exists before using it.",
  "explanation_technical": "In checkout.js line 45, the code attempts to access discount.amount without first validating that discount is not null. When an invalid or expired code is entered, the discount service returns null, leading to a TypeError that propagates as a 500 error.",
  "suggested_fix": "// In src/services/checkout.js\n\nfunction applyDiscount(cart, discountCode) {\n  const discount = discountService.getDiscount(discountCode);\n  \n  // Add null check\n  if (!discount || !discount.isValid()) {\n    throw new ValidationError('Invalid or expired discount code');\n  }\n  \n  return cart.total - discount.amount;\n}",
  "generated_test": "// Test for discount validation\ndescribe('Checkout Service', () => {\n  test('should handle invalid discount code gracefully', async () => {\n    const cart = { total: 100 };\n    const invalidCode = 'EXPIRED123';\n    \n    await expect(\n      checkoutService.applyDiscount(cart, invalidCode)\n    ).rejects.toThrow('Invalid or expired discount code');\n  });\n  \n  test('should handle null discount', async () => {\n    const cart = { total: 100 };\n    const nullCode = null;\n    \n    await expect(\n      checkoutService.applyDiscount(cart, nullCode)\n    ).rejects.toThrow('Invalid or expired discount code');\n  });\n});",
  "processing_time_ms": 8500,
  "created_at": "2026-05-01T15:30:00Z"
}

Response 400:
{
  "error": {
    "code": "PROJECT_NOT_INDEXED",
    "message": "Project must be indexed before analysis"
  }
}
```

### Get Analysis History
```http
GET /analysis/history?project_id=uuid&page=1&limit=10
Authorization: Bearer <token>

Response 200:
{
  "analyses": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "bug_description": "Checkout breaks...",
      "files": ["checkout.js"],
      "root_cause": "...",
      "created_at": "2026-05-01T15:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 10
}
```

### Get Single Analysis
```http
GET /analysis/{analysis_id}
Authorization: Bearer <token>

Response 200:
{
  "id": "uuid",
  "project_id": "uuid",
  "bug_description": "...",
  "files": [...],
  "root_cause": "...",
  "explanation_simple": "...",
  "explanation_technical": "...",
  "suggested_fix": "...",
  "generated_test": "...",
  "processing_time_ms": 8500,
  "created_at": "2026-05-01T15:30:00Z"
}
```

---

## 📊 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid input data |
| INVALID_CREDENTIALS | 401 | Wrong email/password |
| UNAUTHORIZED | 401 | Missing or invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| FILE_TOO_LARGE | 413 | File exceeds size limit |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
| PROJECT_NOT_INDEXED | 400 | Project needs indexing |
| INVALID_REPO_URL | 400 | Invalid GitHub URL |
| INDEXING_IN_PROGRESS | 409 | Already indexing |

---

## 🔒 Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST /auth/login | 5 requests / 15 minutes |
| POST /auth/register | 3 requests / hour |
| POST /analysis/analyze | 10 requests / minute |
| All other endpoints | 100 requests / minute |

---

## 📝 Notes

- All timestamps are in ISO 8601 UTC format
- All IDs are UUIDs
- File uploads limited to 100MB
- Analysis timeout: 30 seconds
- Token expiry: 24 hours