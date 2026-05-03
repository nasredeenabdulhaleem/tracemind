import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  AlertCircle, CheckCircle2, Clock, Copy, Check,
  BugPlay, SearchCode, Wrench, FlaskConical, Lightbulb,
  ChevronDown, ChevronUp,
} from 'lucide-react';

// ─── helpers ────────────────────────────────────────────────────────────────

const SEVERITY_STYLES = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high:     'bg-orange-100 text-orange-700 border-orange-200',
  medium:   'bg-yellow-100 text-yellow-700 border-yellow-200',
  low:      'bg-green-100 text-green-700 border-green-200',
};

const isFailed = (text) =>
  !text ||
  text.trim() === '' ||
  /unable to (generate|determine)/i.test(text) ||
  /generation failed/i.test(text) ||
  /analysis failed/i.test(text);

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={copy}
      className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white transition-colors px-2 py-1 rounded hover:bg-white/10"
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

function CodeBlock({ code, language = '' }) {
  return (
    <div className="relative rounded-xl overflow-hidden border border-gray-800 mt-3">
      <div className="flex items-center justify-between bg-gray-900 px-4 py-2 border-b border-gray-700">
        <span className="text-xs text-gray-400 font-mono">{language || 'code'}</span>
        <CopyButton text={code} />
      </div>
      <pre className="bg-gray-950 text-gray-100 text-xs leading-relaxed p-4 overflow-x-auto">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function MarkdownContent({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="text-sm text-gray-700 leading-relaxed mb-3">{children}</p>,
        h1: ({ children }) => <h1 className="text-base font-bold text-gray-900 mt-4 mb-2">{children}</h1>,
        h2: ({ children }) => <h2 className="text-sm font-bold text-gray-900 mt-4 mb-2 border-b border-gray-100 pb-1">{children}</h2>,
        h3: ({ children }) => <h3 className="text-sm font-semibold text-gray-800 mt-3 mb-1.5">{children}</h3>,
        ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-3">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-3">{children}</ol>,
        li: ({ children }) => <li className="text-sm text-gray-700">{children}</li>,
        strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
        code: ({ inline, className, children }) => {
          if (inline) {
            return <code className="bg-gray-100 text-gray-800 text-xs font-mono px-1.5 py-0.5 rounded">{children}</code>;
          }
          const lang = (className || '').replace('language-', '');
          return <CodeBlock code={String(children).replace(/\n$/, '')} language={lang} />;
        },
        pre: ({ children }) => <>{children}</>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-blue-200 pl-4 my-3 text-sm text-gray-600 italic">{children}</blockquote>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

function SectionStatus({ failed }) {
  return failed
    ? <span className="flex items-center gap-1 text-xs text-red-500"><AlertCircle size={12} /> Failed</span>
    : <span className="flex items-center gap-1 text-xs text-emerald-600"><CheckCircle2 size={12} /> Ready</span>;
}

// ─── tabs config ────────────────────────────────────────────────────────────

const TABS = [
  { id: 'overview',   label: 'Overview',    icon: BugPlay },
  { id: 'rootcause',  label: 'Root Cause',  icon: SearchCode },
  { id: 'fix',        label: 'Suggested Fix', icon: Wrench },
  { id: 'test',       label: 'Test Code',   icon: FlaskConical },
];

// ─── main component ─────────────────────────────────────────────────────────

const AnalysisResults = ({ analysis }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showChunks, setShowChunks] = useState(false);

  const sev = (analysis.severity || 'medium').toLowerCase();
  const sevStyle = SEVERITY_STYLES[sev] || SEVERITY_STYLES.medium;

  const fixFailed  = isFailed(analysis.suggested_fix);
  const testFailed = isFailed(analysis.generated_test);
  const rootFailed = isFailed(analysis.root_cause);

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">

      {/* ── header ── */}
      <div className="px-6 py-4 border-b border-gray-100 flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h2 className="text-base font-semibold text-gray-900 leading-snug truncate">
            {analysis.bug_summary || analysis.bug_description}
          </h2>
          <div className="flex items-center gap-3 mt-1.5 flex-wrap">
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${sevStyle}`}>
              {sev.charAt(0).toUpperCase() + sev.slice(1)}
            </span>
            <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
              {analysis.bug_type}
            </span>
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <Clock size={11} />
              {(analysis.processing_time_ms / 1000).toFixed(1)}s
            </span>
          </div>
        </div>
      </div>

      {/* ── tab nav ── */}
      <div className="flex border-b border-gray-100 overflow-x-auto">
        {TABS.map(({ id, label, icon: Icon }) => {
          const hasFailed =
            (id === 'fix' && fixFailed) ||
            (id === 'test' && testFailed) ||
            (id === 'rootcause' && rootFailed);
          return (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-1.5 px-4 py-3 text-xs font-medium whitespace-nowrap border-b-2 transition-all
                ${activeTab === id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-800'
                }
                ${hasFailed ? 'text-red-400' : ''}
              `}
            >
              <Icon size={13} />
              {label}
              {hasFailed && <AlertCircle size={10} className="text-red-400" />}
            </button>
          );
        })}
      </div>

      {/* ── tab content ── */}
      <div className="p-6 space-y-5">

        {/* OVERVIEW */}
        {activeTab === 'overview' && (
          <>
            {/* Simple explanation card */}
            {analysis.explanation_simple && !isFailed(analysis.explanation_simple) && (
              <div className="flex gap-3 bg-blue-50 border border-blue-100 rounded-xl p-4">
                <Lightbulb size={18} className="text-blue-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-blue-700 mb-1">Plain English Summary</p>
                  <p className="text-sm text-blue-800 leading-relaxed">{analysis.explanation_simple}</p>
                </div>
              </div>
            )}

            {/* Bug description */}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Bug Description</p>
              <p className="text-sm text-gray-700 bg-gray-50 rounded-xl p-4 leading-relaxed">{analysis.bug_description}</p>
            </div>

            {/* Affected components */}
            {analysis.affected_components?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Affected Components</p>
                <div className="flex flex-wrap gap-2">
                  {analysis.affected_components.map((c, i) => (
                    <span key={i} className="bg-gray-100 text-gray-700 text-xs px-2.5 py-1 rounded-lg font-mono">{c}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Relevant files */}
            {analysis.relevant_files?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Relevant Files</p>
                <div className="space-y-1">
                  {analysis.relevant_files.map((f, i) => (
                    <div key={i} className="text-xs text-gray-600 bg-gray-50 border border-gray-100 px-3 py-2 rounded-lg font-mono">{f}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Code chunks toggle */}
            {analysis.code_chunks?.length > 0 && (
              <div>
                <button
                  onClick={() => setShowChunks(v => !v)}
                  className="flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-700 font-medium"
                >
                  {showChunks ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                  {showChunks ? 'Hide' : 'Show'} {analysis.code_chunks.length} retrieved code chunk{analysis.code_chunks.length > 1 ? 's' : ''}
                </button>
                {showChunks && (
                  <div className="mt-3 space-y-3">
                    {analysis.code_chunks.map((chunk, i) => (
                      <div key={i}>
                        <p className="text-xs text-gray-500 font-mono mb-1">
                          {chunk.file_path} {chunk.start_line && `(L${chunk.start_line}–${chunk.end_line})`}
                          {chunk.relevance_score && <span className="ml-2 text-gray-400">score: {chunk.relevance_score.toFixed(3)}</span>}
                        </p>
                        <CodeBlock code={chunk.content} language={chunk.language || ''} />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* ROOT CAUSE */}
        {activeTab === 'rootcause' && (
          <>
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Root Cause Analysis</p>
              <SectionStatus failed={rootFailed} />
            </div>
            {rootFailed
              ? <div className="flex items-center gap-2 bg-red-50 border border-red-100 rounded-xl p-4 text-sm text-red-700">
                  <AlertCircle size={16} /> Unable to determine root cause. Try providing more detail in the bug description.
                </div>
              : <div className="prose-sm max-w-none">
                  <MarkdownContent content={analysis.root_cause} />
                </div>
            }
          </>
        )}

        {/* FIX */}
        {activeTab === 'fix' && (
          <>
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Suggested Fix</p>
              <SectionStatus failed={fixFailed} />
            </div>

            {fixFailed
              ? <div className="flex items-center gap-2 bg-red-50 border border-red-100 rounded-xl p-4 text-sm text-red-700">
                  <AlertCircle size={16} /> Fix generation failed. Retry analysis with a more detailed bug description.
                </div>
              : <>
                  <CodeBlock code={analysis.suggested_fix} language="python" />

                  {analysis.fix_explanation && (
                    <div className="mt-4">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">What Changed &amp; Why</p>
                      <div className="prose-sm max-w-none">
                        <MarkdownContent content={analysis.fix_explanation} />
                      </div>
                    </div>
                  )}

                  {analysis.testing_notes && (
                    <div className="mt-4">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Testing Notes</p>
                      <div className="prose-sm max-w-none">
                        <MarkdownContent content={analysis.testing_notes} />
                      </div>
                    </div>
                  )}
                </>
            }
          </>
        )}

        {/* TEST CODE */}
        {activeTab === 'test' && (
          <>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Generated Test</p>
                {analysis.test_framework && (
                  <span className="text-xs bg-purple-50 text-purple-600 border border-purple-100 px-2 py-0.5 rounded-full">
                    {analysis.test_framework}
                  </span>
                )}
              </div>
              <SectionStatus failed={testFailed} />
            </div>

            {testFailed
              ? <div className="flex items-center gap-2 bg-red-50 border border-red-100 rounded-xl p-4 text-sm text-red-700">
                  <AlertCircle size={16} /> Test generation failed. Retry analysis after a successful fix is generated.
                </div>
              : <CodeBlock code={analysis.generated_test} language={analysis.test_framework === 'jest' ? 'javascript' : 'python'} />
            }
          </>
        )}
      </div>

      {/* ── footer ── */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <p className="text-xs text-gray-400 font-mono">ID: {analysis.analysis_id || analysis.id}</p>
        <p className="text-xs text-gray-400">{new Date(analysis.created_at).toLocaleString()}</p>
      </div>
    </div>
  );
};

export default AnalysisResults;

