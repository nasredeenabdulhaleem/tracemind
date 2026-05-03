# 🚀 PROJECT EXECUTION PROMPT

## Project Name: TraceMind AI

### Natural Language Bug Intelligence System

---

## 🎯 OBJECTIVE

You are tasked with building a **complete, demo-ready web application** that allows users to:

1. Create an account and log in
2. Create a project workspace
3. Connect a GitHub repository OR upload a codebase (ZIP)
4. Index and analyze the codebase
5. Submit a bug description in plain English, logs, or stack traces
6. Receive:

   * Root cause
   * Affected files
   * Explanation (technical + non-technical)
   * Fix suggestion
   * Auto-generated regression test

This system must simulate an **AI-powered debugging assistant** using structured reasoning and agent orchestration.

---

## ⚠️ SCOPE CONTROL (VERY IMPORTANT)

### ✅ START POINT (YOU MUST BUILD)

* Authentication system (JWT-based)
* Project creation and management
* GitHub repo connection OR ZIP upload
* Code ingestion and parsing
* Code indexing (semantic search ready)
* Bug input interface
* AI-powered bug analysis pipeline
* Output display (clean UI card)
* watsonx.ai integration (for reasoning)
* watsonx Orchestrate (for agent flow)

---

### 🚫 STOP POINT (DO NOT BUILD)

* CI/CD pipelines
* Real-time collaboration
* Multi-user teams
* Advanced permissions
* Full GitHub sync automation
* Production-grade scaling infra

👉 Focus on **complete, working POC**, not overengineering.

---

## 🧱 SYSTEM ARCHITECTURE

### Backend: FastAPI

### Frontend: React (Vite + Tailwind)

### Core Flow:

Frontend → FastAPI → watsonx Orchestrate → watsonx.ai → Response

---

## 🧩 CORE MODULES

---

### 1. 🔐 AUTHENTICATION MODULE

#### Features:

* User registration
* Login
* JWT authentication
* Password hashing

#### Backend:

* FastAPI routes:

  * POST `/auth/register`
  * POST `/auth/login`
* Use:

  * `passlib`
  * `python-jose`

#### Frontend:

* Login page
* Signup page
* Token storage (localStorage)

---

### 2. 📁 PROJECT MANAGEMENT MODULE

#### Features:

* Create project
* List user projects
* Select project

#### Backend:

* POST `/projects/create`
* GET `/projects`

#### DB Schema:

```sql
Users
Projects (id, user_id, name, repo_url, created_at)
```

---

### 3. 📦 REPOSITORY INGESTION MODULE

#### Supported Methods:

1. GitHub repo (via URL)
2. ZIP upload

#### Backend:

* POST `/repo/connect`
* POST `/repo/upload`

#### Processing:

* Clone repo OR extract ZIP
* Store in `/data/projects/{project_id}`

#### Tools:

* `GitPython`
* `zipfile`

---

### 4. 🧠 CODE PARSING + INDEXING ENGINE

#### Objective:

Convert codebase into searchable structure

#### Steps:

1. Traverse files
2. Extract functions/classes
3. Chunk code logically
4. Generate embeddings
5. Store in vector DB

#### Tools:

* `tree-sitter` or `libcst`
* `FAISS` (vector search)

#### Storage:

* Vector DB: embeddings
* PostgreSQL: metadata

---

### 5. 🐞 BUG INPUT MODULE

#### Endpoint:

POST `/analyze`

#### Input:

```json
{
  "project_id": "...",
  "query": "Checkout breaks after discount code"
}
```

#### Responsibilities:

* Normalize input
* Detect type (log, stack trace, plain text)
* Forward to agent pipeline

---

### 6. 🤖 AI AGENT SYSTEM (CRITICAL CORE)

You MUST implement an **agent-based reasoning system** using:

* IBM watsonx Orchestrate (workflow)
* IBM watsonx.ai (Granite models)

---

### AGENT DEFINITIONS

#### 1. Bug Understanding Agent

* Converts input into structured intent
* Identifies suspected module

---

#### 2. Code Retrieval Agent

* Queries FAISS vector DB
* Returns top relevant code chunks

---

#### 3. Root Cause Agent

* Combines:

  * bug intent
  * retrieved code
* Outputs:

  * root cause
  * reasoning

---

#### 4. Fix Generator Agent

* Generates:

  * code patch
  * explanation

---

#### 5. Test Generator Agent

* Generates:

  * regression test
  * edge cases

---

### Orchestration Flow:

Bug Input
→ Understanding Agent
→ Retrieval Agent
→ Root Cause Agent
→ Fix Agent
→ Test Agent
→ Final Output

---

### 7. 🧾 RESPONSE FORMAT

Return structured JSON:

```json
{
  "files": ["checkoutService.js"],
  "root_cause": "...",
  "explanation_simple": "...",
  "explanation_technical": "...",
  "fix": "...",
  "test": "..."
}
```

---

### 8. 🎨 FRONTEND (React)

#### Pages:

* Login / Signup
* Dashboard
* Project View
* Bug Analysis Screen

---

### Main UI (Single Screen Focus):

#### Components:

* Input box (bug description)
* Submit button
* Output card:

  * Files
  * Root cause
  * Fix
  * Test

---

### UX RULES (STRICT):

* Minimal navigation
* One primary action per screen
* Show loading state
* Use clear labels
* Avoid technical overload

---

## 🧠 HCI + PSYCHOLOGICAL DESIGN

You MUST implement:

### 1. Cognitive Simplicity

* No clutter
* Clear outputs

### 2. Trust Indicators

* Show file names
* Show reasoning steps

### 3. Feedback Loop

* “Analyzing your bug...”

### 4. Accessibility

* Non-technical explanation included

---

## ⚙️ TECH STACK

### Backend:

* FastAPI
* PostgreSQL
* FAISS
* GitPython
* tree-sitter

### Frontend:

* React (Vite)
* TailwindCSS
* Axios

### AI:

* watsonx.ai (Granite models)
* watsonx Orchestrate (agent flows)

---

## 🪜 STEP-BY-STEP EXECUTION PLAN

### Phase 1:

* Setup backend + frontend

### Phase 2:

* Auth system

### Phase 3:

* Project system

### Phase 4:

* Repo ingestion

### Phase 5:

* Code parsing + indexing

### Phase 6:

* AI agent integration

### Phase 7:

* UI output

### Phase 8:

* Testing + polish

---

## 🏁 DEFINITION OF DONE

The system is COMPLETE when:

✅ User logs in
✅ Creates project
✅ Uploads or connects repo
✅ System indexes code
✅ User submits bug
✅ System returns:

* root cause
* fix
* test

✅ UI is clean and demo-ready

---

## 🎤 DEMO REQUIREMENT

The system must:

* Work in under 10 seconds per query
* Handle a real repo
* Produce believable outputs

---

## 🧠 FINAL INSTRUCTION

Focus on:

* CLARITY over complexity
* COMPLETENESS over features
* DEMO EXPERIENCE over perfection

You are building a **hackathon-winning AI product**, not a production SaaS.

---
note we will be making use lts packages no deprecated packages and we will be writing secure and clean code with security in mind  ensure app is water tight, ## ☁️ CLOUD STORAGE INTEGRATION (MANDATORY)

### Using Cloudflare R2 (S3-Compatible Object Storage)

---

## 🎯 OBJECTIVE

You MUST implement cloud-based storage for all uploaded and connected repositories using **Cloudflare R2**.

The system must:

* Store all repositories in R2 as ZIP archives
* Use temporary local processing (ephemeral workspace)
* Never persist full repositories on the backend server long-term
* Ensure the backend remains **stateless and scalable**

---

## 🧱 STORAGE ARCHITECTURE

### Bucket Name:

```plaintext
tracemind-projects
```

---

### Object Key Structure:

```plaintext
/projects/{user_id}/{project_id}/repo.zip
```

Example:

```plaintext
/projects/user_123/project_456/repo.zip
```

---

## 🔐 ACCESS CONTROL RULES

* All buckets MUST be private
* Do NOT expose raw file URLs
* Use signed URLs if access is required (optional for MVP)
* Credentials MUST be stored in environment variables

---

## ⚙️ ENVIRONMENT CONFIGURATION

You MUST configure R2 using environment variables:

```env
R2_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=tracemind-projects
```

---

## 🧰 REQUIRED LIBRARY

Use:

```bash
pip install boto3
```

Even though this is R2, it is **S3-compatible**, so you MUST use `boto3`.

---

## 🧩 IMPLEMENTATION REQUIREMENTS

You MUST create a dedicated service:

### 📦 RepoStorageService

This service handles all interactions with R2.

---

### REQUIRED METHODS

#### 1. upload_repo(file_path, user_id, project_id)

* Compress repo into ZIP (if not already zipped)
* Upload to R2
* Return object key

---

#### 2. download_repo(user_id, project_id, local_path)

* Download repo.zip from R2
* Save into temporary directory

---

#### 3. delete_temp(local_path)

* Remove all temporary files after processing

---

## 🧪 TEMPORARY PROCESSING WORKSPACE

All processing MUST occur in:

```bash
/tmp/tracemind/{project_id}/
```

---

### RULES:

* This directory is ephemeral
* It MUST be deleted after indexing is complete
* NEVER store long-term data here

---

## 🔁 REPO INGESTION FLOW (STRICT)

### For GitHub Repos:

1. Clone repository to temp directory
2. Compress into ZIP
3. Upload ZIP to R2
4. Delete local clone

---

### For ZIP Uploads:

1. Receive file
2. Upload directly to R2
3. Do NOT store permanently on server

---

## 🧠 INDEXING FLOW (STRICT)

1. Download repo.zip from R2
2. Extract into `/tmp/tracemind/{project_id}/`
3. Parse and chunk code
4. Generate embeddings
5. Store embeddings in vector DB
6. DELETE temp directory completely

---

## ⚠️ NON-NEGOTIABLE RULES

* NEVER analyze directly from R2
* ALWAYS download to temp workspace first
* NEVER keep full repo on backend disk after processing
* ALWAYS clean up temp files

---

## 🧠 DESIGN JUSTIFICATION (IMPORTANT FOR DEMO)

This architecture ensures:

* Stateless backend design
* Scalable storage independent of compute
* Efficient processing using temporary environments
* Clean separation between storage and computation

---

## 🎤 DEMO EXPLANATION (YOU MUST ENABLE THIS)

The system should allow this explanation:

> “We store repositories in Cloudflare R2, an S3-compatible object storage. When analysis is required, we temporarily pull the repository into an ephemeral processing environment, index it, and discard the local copy—ensuring a stateless and scalable architecture.”

---

## 🚀 SUCCESS CRITERIA

This feature is COMPLETE when:

* Repositories are stored in R2
* Backend does NOT persist repos locally
* Temporary processing works correctly
* Indexing pipeline works from R2 source
* System cleans up all temp files

---
{"email":"test2@example.com","password":"Test1234!"}