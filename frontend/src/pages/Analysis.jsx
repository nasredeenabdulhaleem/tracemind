import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { toast } from 'sonner';
import { projectsAPI, analysisAPI } from '../services/api';
import Navbar from '../components/common/Navbar';
import AnalysisForm from '../components/analysis/AnalysisForm';
import AnalysisResults from '../components/analysis/AnalysisResults';
import AgentProgress from '../components/analysis/AgentProgress';
import {
  Clock, AlertCircle, CheckCircle2, History, ChevronRight, Loader2,
} from 'lucide-react';

const SEVERITY_DOT = {
  critical: 'bg-red-500',
  high:     'bg-orange-400',
  medium:   'bg-yellow-400',
  low:      'bg-green-500',
};

function HistoryItem({ item, isActive, onClick }) {
  const dot = SEVERITY_DOT[(item.severity || 'medium').toLowerCase()] || SEVERITY_DOT.medium;
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-3 rounded-xl border transition-all group
        ${isActive
          ? 'border-blue-200 bg-blue-50'
          : 'border-transparent hover:border-gray-100 hover:bg-gray-50'
        }`}
    >
      <div className="flex items-start gap-2.5">
        <span className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${dot}`} />
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium text-gray-800 leading-snug line-clamp-2">
            {item.bug_summary || item.bug_description}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <Clock size={10} className="text-gray-400" />
            <span className="text-xs text-gray-400">
              {new Date(item.created_at).toLocaleString(undefined, {
                month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit',
              })}
            </span>
            {item.processing_time_ms && (
              <span className="text-xs text-gray-300">
                · {(item.processing_time_ms / 1000).toFixed(1)}s
              </span>
            )}
          </div>
        </div>
        <ChevronRight size={12} className="text-gray-300 group-hover:text-gray-500 shrink-0 mt-1 transition-colors" />
      </div>
    </button>
  );
}

const Analysis = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [stepState, setStepState] = useState({});
  const [streamError, setStreamError] = useState(null);
  const streamControllerRef = useRef(null);

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [activeHistoryId, setActiveHistoryId] = useState(null);
  const [historyLoadingId, setHistoryLoadingId] = useState(null);

  useEffect(() => {
    loadProject();
    loadHistory();
  }, [id]);

  const loadProject = async () => {
    try {
      const response = await projectsAPI.get(id);
      setProject(response.data);
    } catch {
      toast.error('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const response = await analysisAPI.getHistory(id, { page: 1, page_size: 20 });
      setHistory(response.data.analyses || []);
    } catch {
      // history panel is non-critical; swallow error silently
    } finally {
      setHistoryLoading(false);
    }
  }, [id]);

  const loadHistoryItem = async (item) => {
    if (activeHistoryId === item.id) return;
    setHistoryLoadingId(item.id);
    try {
      const response = await analysisAPI.get(item.id);
      setAnalysis(response.data);
      setActiveHistoryId(item.id);
    } catch {
      toast.error('Failed to load analysis');
    } finally {
      setHistoryLoadingId(null);
    }
  };

  const handleAnalyze = async (bugDescription) => {
    // Abort any in-flight stream
    if (streamControllerRef.current) {
      streamControllerRef.current.abort();
    }

    setAnalyzing(true);
    setAnalysis(null);
    setActiveHistoryId(null);
    setStepState({});
    setStreamError(null);

    const controller = analysisAPI.analyzeStream(
      { project_id: id, bug_description: bugDescription },
      (event) => {
        if (event.type === 'progress') {
          setStepState((prev) => ({ ...prev, [event.step]: event.status }));
        } else if (event.type === 'result') {
          setAnalysis(event.data);
          toast.success('Analysis complete');
          loadHistory();
          setAnalyzing(false);
        } else if (event.type === 'error') {
          setStreamError(event.message);
          toast.error(event.message || 'Analysis failed');
          setAnalyzing(false);
        } else if (event.type === 'done') {
          setAnalyzing(false);
        }
      }
    );
    streamControllerRef.current = controller;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <Navbar />
        <div className="flex flex-col items-center justify-center h-[60vh] gap-3">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
          <p className="text-sm text-gray-500">Loading…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Navbar />

      <div className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link
          to={`/projects/${id}`}
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors mb-6"
        >
          ← Back to Project
        </Link>

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Bug Analysis</h1>
          <p className="text-sm text-gray-500 mt-0.5">{project?.name}</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[1fr_2fr_280px] gap-6">

          {/* ── Left: form ── */}
          <div className="space-y-4">
            <AnalysisForm onSubmit={handleAnalyze} loading={analyzing} />
          </div>

          {/* ── Center: results ── */}
          <div>
            {analyzing ? (
              <AgentProgress stepState={stepState} errorMessage={streamError} />
            ) : analysis ? (
              <AnalysisResults analysis={analysis} />
            ) : (
              <div className="bg-white rounded-2xl border border-dashed border-gray-200 p-8 flex flex-col items-center justify-center text-center h-full min-h-[280px]">
                <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center mb-3">
                  <AlertCircle size={22} className="text-gray-300" />
                </div>
                <p className="text-sm text-gray-400">Describe a bug and click Analyze Bug</p>
                <p className="text-xs text-gray-300 mt-1">Results will appear here</p>
              </div>
            )}
          </div>

          {/* ── Right: history ── */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 h-fit max-h-[calc(100vh-180px)] flex flex-col">
            <div className="flex items-center gap-2 mb-3 shrink-0">
              <History size={14} className="text-gray-400" />
              <p className="text-xs font-semibold text-gray-700">Analysis History</p>
              {history.length > 0 && (
                <span className="ml-auto text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-full">{history.length}</span>
              )}
            </div>

            <div className="overflow-y-auto flex-1 space-y-1 pr-0.5">
              {historyLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 size={18} className="animate-spin text-gray-300" />
                </div>
              ) : history.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-xs text-gray-400">No analyses yet</p>
                  <p className="text-xs text-gray-300 mt-0.5">Run your first analysis above</p>
                </div>
              ) : (
                history.map((item) => (
                  <div key={item.id} className="relative">
                    {historyLoadingId === item.id && (
                      <div className="absolute inset-0 flex items-center justify-center bg-white/70 rounded-xl z-10">
                        <Loader2 size={14} className="animate-spin text-blue-500" />
                      </div>
                    )}
                    <HistoryItem
                      item={item}
                      isActive={activeHistoryId === item.id}
                      onClick={() => loadHistoryItem(item)}
                    />
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analysis;

