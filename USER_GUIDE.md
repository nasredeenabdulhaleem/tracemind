# TraceMind AI - User Guide

## Getting Started

TraceMind AI is an intelligent bug analysis tool that uses AI agents to understand, locate, and fix bugs in your codebase.

## Quick Start

### 1. Create Account
1. Navigate to the app
2. Click "Sign up"
3. Enter email, username, and password
4. Click "Create Account"

### 2. Login
1. Enter your email and password
2. Click "Sign In"

## Managing Projects

### Create a Project
1. Click "+ New Project" on dashboard
2. Enter project name and description
3. Select repository type (ZIP or GitHub)
4. Click "Create Project"

### Upload Code
**ZIP Upload:**
1. Open project details
2. Click "Choose File"
3. Select ZIP file (max 100MB)
4. Click "Upload Repository"

**GitHub (if configured):**
1. Enter repository URL
2. Click "Connect GitHub"

### Process Code
After upload, follow these steps:

**Step 1: Parse Code**
- Extracts functions, classes, and code chunks
- Click "Parse" button
- Wait for completion (1-2 minutes)

**Step 2: Create Index**
- Builds vector embeddings for search
- Click "Index" button
- Wait for completion (2-5 minutes)

**Step 3: Ready for Analysis**
- Project is now ready
- Click "Analyze" to start bug analysis

## Bug Analysis

### Submit Bug Report
1. Navigate to project
2. Click "Analyze" button
3. Enter bug description:
   - Be specific about the issue
   - Include error messages
   - Describe expected vs actual behavior
4. Click "Analyze Bug"

### Understanding Results

**Overview Tab:**
- Bug description summary
- Affected files list
- Simple explanation for non-technical users

**Root Cause Tab:**
- Detailed root cause analysis
- Technical explanation
- Why the bug occurs

**Suggested Fix Tab:**
- Code changes to fix the bug
- Implementation details
- Best practices applied

**Test Code Tab:**
- Generated test cases
- Validation code
- How to verify the fix

### Example Bug Descriptions

Good examples:
- "User authentication fails after password reset with 401 error"
- "Payment processing returns 500 error when applying discount codes"
- "Dashboard takes 30+ seconds to load with 1000+ records"

Poor examples:
- "It doesn't work"
- "Error on page"
- "Fix the bug"

## Best Practices

### Project Organization
- One project per repository
- Keep projects updated
- Delete unused projects

### Bug Descriptions
- Be specific and detailed
- Include error messages
- Mention affected features
- Describe steps to reproduce

### Code Upload
- Remove sensitive data before upload
- Exclude node_modules, .git folders
- Keep files under 100MB
- Use clean, recent code

## Tips & Tricks

### Faster Analysis
- Index your code once
- Reuse indexed projects
- Provide clear bug descriptions

### Better Results
- Include error stack traces
- Mention affected files if known
- Describe expected behavior
- Add reproduction steps

### Managing Storage
- Delete old projects
- Re-upload only when code changes significantly
- Use GitHub integration for automatic updates

## Troubleshooting

### Upload Fails
- Check file size (max 100MB)
- Ensure ZIP format
- Remove large binary files
- Check internet connection

### Parsing Takes Too Long
- Large codebases take longer
- Wait up to 5 minutes
- Refresh page to check status

### Analysis Errors
- Ensure project is indexed
- Check bug description clarity
- Verify watsonx.ai credits
- Try again with more details

### No Results
- Make bug description more specific
- Ensure affected files are in project
- Check if code was parsed correctly
- Verify indexing completed

## Keyboard Shortcuts

- `Ctrl/Cmd + K` - Create new project
- `Ctrl/Cmd + /` - Search projects
- `Esc` - Close modals

## Support

Need help?
- Check [Setup Guide](SETUP_GUIDE.md)
- Review [API Docs](API_SPECIFICATION.md)
- Report issues on GitHub