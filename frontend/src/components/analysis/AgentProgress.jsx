import { CheckCircle2, Loader2, XCircle, Clock } from 'lucide-react';

const AGENTS = [
  {
    key: 'bug_understanding',
    label: 'Bug Understanding',
    desc: 'Parsing your bug description and extracting intent',
  },
  {
    key: 'code_retrieval',
    label: 'Code Retrieval',
    desc: 'Searching the codebase for relevant files',
  },
  {
    key: 'root_cause_analysis',
    label: 'Root Cause Analysis',
    desc: 'Tracing why the bug happens',
  },
  {
    key: 'fix_generation',
    label: 'Fix Generation',
    desc: 'Writing a code fix for the issue',
  },
  {
    key: 'test_generation',
    label: 'Test Generation',
    desc: 'Generating regression tests',
  },
];

function StepRow({ agent, stepState }) {
  const state = stepState[agent.key] || 'pending';

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-300 ${
        state === 'running'
          ? 'bg-blue-50 border-blue-200 shadow-sm'
          : state === 'completed'
          ? 'bg-emerald-50 border-emerald-200'
          : state === 'failed'
          ? 'bg-red-50 border-red-200'
          : 'bg-gray-50 border-gray-100'
      }`}
    >
      {/* Icon */}
      <div className="shrink-0 w-8 h-8 flex items-center justify-center">
        {state === 'running' && (
          <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
        )}
        {state === 'completed' && (
          <CheckCircle2 className="w-5 h-5 text-emerald-500" />
        )}
        {state === 'failed' && (
          <XCircle className="w-5 h-5 text-red-500" />
        )}
        {state === 'pending' && (
          <Clock className="w-5 h-5 text-gray-300" />
        )}
      </div>

      {/* Text */}
      <div className="min-w-0 flex-1">
        <p
          className={`text-sm font-semibold leading-snug ${
            state === 'running'
              ? 'text-blue-700'
              : state === 'completed'
              ? 'text-emerald-700'
              : state === 'failed'
              ? 'text-red-600'
              : 'text-gray-400'
          }`}
        >
          {agent.label}
        </p>
        <p
          className={`text-xs mt-0.5 ${
            state === 'running'
              ? 'text-blue-500'
              : state === 'completed'
              ? 'text-emerald-600'
              : state === 'failed'
              ? 'text-red-400'
              : 'text-gray-300'
          }`}
        >
          {state === 'running'
            ? agent.desc
            : state === 'completed'
            ? 'Done'
            : state === 'failed'
            ? 'Failed'
            : 'Waiting…'}
        </p>
      </div>

      {/* State badge */}
      <div className="shrink-0">
        {state === 'running' && (
          <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-600 uppercase tracking-wide">
            Running
          </span>
        )}
        {state === 'completed' && (
          <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-600 uppercase tracking-wide">
            Done
          </span>
        )}
        {state === 'failed' && (
          <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-red-100 text-red-500 uppercase tracking-wide">
            Failed
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * stepState: Record<agentKey, 'pending'|'running'|'completed'|'failed'>
 */
export default function AgentProgress({ stepState = {}, errorMessage = null }) {
  const completedCount = AGENTS.filter((a) => stepState[a.key] === 'completed').length;
  const total = AGENTS.length;

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-sm font-semibold text-gray-800">Running AI Pipeline</p>
          <p className="text-xs text-gray-400 mt-0.5">
            {errorMessage
              ? 'An error occurred'
              : completedCount === total
              ? 'All agents finished — loading results…'
              : `${completedCount} of ${total} agents complete`}
          </p>
        </div>
        {!errorMessage && (
          <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">
            {completedCount}/{total}
          </span>
        )}
      </div>

      {/* Progress bar */}
      {!errorMessage && (
        <div className="w-full h-1.5 bg-gray-100 rounded-full mb-5 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-500"
            style={{ width: `${(completedCount / total) * 100}%` }}
          />
        </div>
      )}

      {/* Error banner */}
      {errorMessage && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-xs text-red-600">
          {errorMessage}
        </div>
      )}

      {/* Steps */}
      <div className="space-y-2">
        {AGENTS.map((agent) => (
          <StepRow key={agent.key} agent={agent} stepState={stepState} />
        ))}
      </div>
    </div>
  );
}
