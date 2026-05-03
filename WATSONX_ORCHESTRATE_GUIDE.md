# watsonx Orchestrate Integration Guide

## Overview

TraceMind AI now uses **watsonx Orchestrate** for managing the multi-agent workflow for bug analysis. This provides enterprise-grade workflow orchestration with:

- **Dependency Management**: Automatic handling of step dependencies
- **Progress Tracking**: Real-time workflow status monitoring
- **Error Recovery**: Graceful handling of failures with detailed error reporting
- **Performance Metrics**: Detailed timing for each workflow step
- **Scalability**: Ready for parallel execution and distributed processing

## Architecture

### Workflow Steps

The bug analysis workflow consists of 5 sequential steps:

```
1. Bug Understanding
   ↓
2. Code Retrieval (with Vector Search)
   ↓
3. Root Cause Analysis
   ↓
4. Fix Generation
   ↓
5. Test Generation
```

### Service Structure

```
WatsonxOrchestrateService
├── WorkflowStep (for each agent)
│   ├── name: Step display name
│   ├── agent: AI agent instance
│   ├── dependencies: Required previous steps
│   ├── status: pending/running/completed/failed
│   └── timing: start_time, end_time, duration
│
└── execute_workflow()
    ├── Validates dependencies
    ├── Executes steps sequentially
    ├── Tracks progress
    ├── Aggregates results
    └── Stores in database
```

## Usage

### Basic Usage

```python
from app.services.orchestrate_service import WatsonxOrchestrateService

# Initialize service
orchestrate = WatsonxOrchestrateService()

# Execute workflow
result = orchestrate.execute_workflow(
    bug_description="Application crashes when clicking submit button",
    project_id="project-uuid",
    user_id="user-uuid",
    db=db_session
)

# Access results
print(result["bug_summary"])
print(result["root_cause"])
print(result["suggested_fix"])
print(result["generated_test"])

# Check workflow metadata
print(result["workflow"]["total_time_ms"])
for step in result["workflow"]["steps"]:
    print(f"{step['name']}: {step['duration_ms']}ms")
```

### With Progress Callback

```python
def progress_callback(update):
    print(f"Step: {update['step']}")
    print(f"Status: {update['status']}")
    print(f"Message: {update['message']}")

result = orchestrate.execute_workflow(
    bug_description="Memory leak in user service",
    project_id="project-uuid",
    user_id="user-uuid",
    db=db_session,
    callback=progress_callback
)
```

### Get Workflow Status

```python
# Get current workflow status
status = orchestrate.get_workflow_status()

print(f"Overall Status: {status['overall_status']}")
for step in status['steps']:
    print(f"{step['name']}: {step['status']}")
```

## API Response Format

### Success Response

```json
{
  "analysis_id": "uuid",
  "bug_description": "Original bug description",
  "bug_summary": "AI-generated summary",
  "affected_components": ["component1", "component2"],
  "bug_type": "logic_error",
  "severity": "high",
  "relevant_files": ["file1.py", "file2.py"],
  "code_chunks": [
    {
      "file_path": "src/app.py",
      "start_line": 10,
      "end_line": 25,
      "content": "...",
      "language": "python",
      "score": 0.95
    }
  ],
  "root_cause": "Detailed root cause explanation",
  "explanation_technical": "Technical explanation",
  "suggested_fix": "Code fix with explanation",
  "explanation_simple": "Simple explanation for non-technical users",
  "generated_test": "Test code",
  "test_framework": "pytest",
  "processing_time_ms": 5432,
  "created_at": "2026-05-01T19:00:00Z",
  "workflow": {
    "total_time_ms": 5432,
    "status": "completed",
    "steps": [
      {
        "name": "Bug Understanding",
        "status": "completed",
        "dependencies": [],
        "start_time": "2026-05-01T19:00:00Z",
        "end_time": "2026-05-01T19:00:01Z",
        "duration_ms": 1200,
        "error": null
      },
      {
        "name": "Code Retrieval",
        "status": "completed",
        "dependencies": ["bug_understanding"],
        "start_time": "2026-05-01T19:00:01Z",
        "end_time": "2026-05-01T19:00:02Z",
        "duration_ms": 800,
        "error": null
      },
      {
        "name": "Root Cause Analysis",
        "status": "completed",
        "dependencies": ["bug_understanding", "code_retrieval"],
        "start_time": "2026-05-01T19:00:02Z",
        "end_time": "2026-05-01T19:00:04Z",
        "duration_ms": 1500,
        "error": null
      },
      {
        "name": "Fix Generation",
        "status": "completed",
        "dependencies": ["bug_understanding", "root_cause_analysis"],
        "start_time": "2026-05-01T19:00:04Z",
        "end_time": "2026-05-01T19:00:05Z",
        "duration_ms": 1200,
        "error": null
      },
      {
        "name": "Test Generation",
        "status": "completed",
        "dependencies": ["fix_generation"],
        "start_time": "2026-05-01T19:00:05Z",
        "end_time": "2026-05-01T19:00:05.5Z",
        "duration_ms": 732,
        "error": null
      }
    ]
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "WORKFLOW_FAILED",
    "message": "Workflow execution failed at step: root_cause_analysis",
    "details": "watsonx.ai API timeout"
  },
  "workflow": {
    "status": "failed",
    "steps": [
      {
        "name": "Bug Understanding",
        "status": "completed",
        "duration_ms": 1200
      },
      {
        "name": "Code Retrieval",
        "status": "completed",
        "duration_ms": 800
      },
      {
        "name": "Root Cause Analysis",
        "status": "failed",
        "error": "watsonx.ai API timeout",
        "duration_ms": 30000
      }
    ]
  }
}
```

## Configuration

### Environment Variables

```bash
# watsonx.ai Configuration
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Optional: Workflow Timeouts
MAX_ANALYSIS_TIME=30  # seconds per step
MAX_WORKFLOW_TIME=120  # seconds total
```

### Custom Workflow Configuration

You can customize the workflow by modifying `orchestrate_service.py`:

```python
# Add new step
self.workflow_steps["custom_step"] = WorkflowStep(
    name="Custom Analysis",
    agent=CustomAgent(),
    dependencies=["bug_understanding"]
)

# Modify execution order
# Steps execute based on dependency graph
```

## Performance Optimization

### Parallel Execution (Future Enhancement)

```python
# Execute independent steps in parallel
async def execute_parallel_steps(self, steps: List[str]):
    tasks = [self._execute_step(step, context) for step in steps]
    results = await asyncio.gather(*tasks)
    return results
```

### Caching

```python
# Cache analysis results for similar bugs
from app.services.cache_service import CacheService

cache = CacheService()
cached_result = cache.get_cached_analysis(project_id, bug_hash)
if cached_result:
    return cached_result
```

## Monitoring & Debugging

### Logging

All workflow steps are logged with detailed information:

```python
logger.info("Starting watsonx Orchestrate workflow execution")
logger.info(f"Executing step: {step.name}")
logger.info(f"Workflow completed successfully in {total_time_ms}ms")
logger.error(f"Workflow execution failed: {error}")
```

### Metrics

Track workflow performance:

```python
# Average processing time per step
# Success/failure rates
# Most common failure points
# Resource utilization
```

## Best Practices

1. **Error Handling**: Always wrap workflow execution in try-catch
2. **Timeouts**: Set appropriate timeouts for each step
3. **Progress Updates**: Use callbacks for long-running workflows
4. **Resource Management**: Clean up resources after workflow completion
5. **Monitoring**: Track workflow metrics for optimization

## Troubleshooting

### Common Issues

**Issue**: Workflow times out
- **Solution**: Increase `MAX_WORKFLOW_TIME` or optimize agent prompts

**Issue**: Step fails with dependency error
- **Solution**: Check that all required steps completed successfully

**Issue**: watsonx.ai API errors
- **Solution**: Verify API credentials and check rate limits

## Migration from Custom Orchestration

The new watsonx Orchestrate service maintains backward compatibility:

```python
# Old way (still works)
from app.services.analysis_service import AnalysisOrchestrationService
service = AnalysisOrchestrationService()
result = service.analyze_bug(...)

# New way (recommended)
from app.services.orchestrate_service import WatsonxOrchestrateService
orchestrate = WatsonxOrchestrateService()
result = orchestrate.execute_workflow(...)
```

## Future Enhancements

- [ ] Parallel step execution for independent tasks
- [ ] Workflow versioning and A/B testing
- [ ] Custom workflow templates
- [ ] Integration with watsonx Orchestrate UI
- [ ] Advanced error recovery strategies
- [ ] Workflow analytics dashboard

## Support

For issues or questions:
- Check logs in `/var/log/tracemind/`
- Review workflow status in response
- Contact support with `analysis_id` for debugging

---

**Last Updated**: 2026-05-01  
**Version**: 1.0.0  
**Status**: Production Ready