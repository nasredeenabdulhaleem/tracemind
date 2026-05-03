import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'sonner';
import {
  ArrowLeft, FolderOpen, ChevronRight,
  CheckCircle2, Circle, Loader2, AlertCircle, RefreshCw,
  Code2, Database, Zap, Github, FileArchive, RotateCcw,
  ExternalLink,
} from 'lucide-react';
import { projectsAPI, parsingAPI, indexingAPI } from '../services/api';
import Navbar from '../components/common/Navbar';
import ImportRepository from '../components/project/ImportRepository';

const STEP_ICONS = { upload: FolderOpen, parse: Code2, index: Database, analyze: Zap };

const StepStatus = ({ status }) => {
  if (status === 'completed') return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
  if (status === 'processing') return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
  if (status === 'failed') return <AlertCircle className="w-5 h-5 text-red-500" />;
  return <Circle className="w-5 h-5 text-gray-300" />;
};

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [parsing, setParsing] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [showReplace, setShowReplace] = useState(false);
  const pollRef = useRef(null);

  useEffect(() => {
    loadProject();
    return () => clearInterval(pollRef.current);
  }, [id]);

  const loadProject = async (silent = false) => {
    try {
      const response = await projectsAPI.get(id);
      const p = response.data;
      setProject(p);

      // Auto-poll while processing
      if (p.indexing_status === 'processing') {
        if (!pollRef.current) {
          pollRef.current = setInterval(() => loadProject(true), 3000);
        }
      } else {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    } catch (error) {
      if (!silent) {
        toast.error('Failed to load project');
        navigate('/');
      }
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    toast.success('Repository uploaded successfully');
    setShowReplace(false);
    loadProject();
  };

  const handleParse = async () => {
    setParsing(true);
    const toastId = toast.loading('Starting code parser…');
    try {
      await parsingAPI.parse(id);
      toast.success('Parsing started — tracking progress', { id: toastId });
      loadProject(true);
      pollRef.current = setInterval(() => loadProject(true), 3000);
    } catch (error) {
      const msg = error.response?.data?.detail || 'Failed to start parsing';
      toast.error(msg, { id: toastId });
    } finally {
      setParsing(false);
    }
  };

  const handleIndex = async () => {
    setIndexing(true);
    const toastId = toast.loading('Building vector index…');
    try {
      await indexingAPI.createIndex(id);
      toast.success('Indexing started — tracking progress', { id: toastId });
      loadProject(true);
      pollRef.current = setInterval(() => loadProject(true), 3000);
    } catch (error) {
      const msg = error.response?.data?.detail || 'Failed to start indexing';
      toast.error(msg, { id: toastId });
    } finally {
      setIndexing(false);
    }
  };

  const getSteps = (p) => {
    if (!p) return [];
    const uploaded = !!p.r2_object_key;
    const parsed = p.indexing_status === 'completed' || p.is_indexed;
    const indexed = p.is_indexed;
    const processing = p.indexing_status === 'processing';
    const failed = p.indexing_status === 'failed';

    return [
      {
        key: 'upload',
        label: 'Import Repository',
        desc: p.repo_type === 'github' ? 'GitHub repository cloned' : p.repo_type === 'zip' ? 'ZIP archive uploaded' : 'Upload or connect a repository',
        status: uploaded ? 'completed' : 'pending',
        Icon: FolderOpen,
      },
      {
        key: 'parse',
        label: 'Parse & Index Code',
        desc: 'Extract code chunks and build semantic search index',
        status: !uploaded ? 'pending' : processing ? 'processing' : failed ? 'failed' : parsed ? 'completed' : 'pending',
        Icon: Code2,
      },
      {
        key: 'analyze',
        label: 'Analyze Bugs',
        desc: 'Run AI-powered root cause analysis',
        status: parsed ? 'ready' : 'pending',
        Icon: Zap,
      },
    ];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <Navbar />
        <div className="flex items-center justify-center h-[60vh]">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
            <p className="text-sm text-gray-500">Loading project…</p>
          </div>
        </div>
      </div>
    );
  }

  const steps = getSteps(project);
  const statusColor = {
    completed: 'bg-emerald-50 border-emerald-200',
    processing: 'bg-blue-50 border-blue-200',
    failed: 'bg-red-50 border-red-200',
    ready: 'bg-violet-50 border-violet-200',
    pending: 'bg-gray-50 border-gray-200',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Projects
        </Link>

        {/* Header card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                <FolderOpen className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
                <p className="text-sm text-gray-500 mt-0.5">
                  {project.description || 'No description provided'}
                </p>
              </div>
            </div>
            <button
              onClick={() => loadProject()}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

        {/* Repo source + replace button */}
          {project.r2_object_key && (
            <div className="flex items-center gap-2 mt-3 flex-wrap">
              {project.repo_type === 'github' && project.repo_url ? (
                <a
                  href={project.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 bg-gray-50 border border-gray-200 px-2.5 py-1 rounded-lg transition-colors"
                >
                  <Github size={11} />
                  <span className="max-w-[200px] truncate">
                    {project.repo_url.replace('https://github.com/', '')}
                  </span>
                  <ExternalLink size={10} className="shrink-0" />
                </a>
              ) : project.repo_type === 'zip' ? (
                <span className="inline-flex items-center gap-1.5 text-xs text-gray-500 bg-gray-50 border border-gray-200 px-2.5 py-1 rounded-lg">
                  <FileArchive size={11} /> ZIP Upload
                </span>
              ) : null}
              <button
                onClick={() => setShowReplace((v) => !v)}
                className="inline-flex items-center gap-1.5 text-xs text-gray-400 hover:text-amber-600 transition-colors"
              >
                <RotateCcw size={11} />
                {showReplace ? 'Cancel replace' : 'Replace repository'}
              </button>
            </div>
          )}

          {/* Status pills */}
          <div className="flex gap-2 mt-3 flex-wrap">
            {project.r2_object_key && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5" /> Repository Uploaded
              </span>
            )}
            {project.indexing_status === 'processing' && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing…
              </span>
            )}
            {project.indexing_status === 'completed' && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5" /> Parsed & Indexed
              </span>
            )}
            {project.indexing_status === 'completed' && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-violet-100 text-violet-700">
                <Zap className="w-3.5 h-3.5" /> Ready for Analysis
              </span>
            )}
            {project.indexing_status === 'failed' && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                <AlertCircle className="w-3.5 h-3.5" /> Parse Failed
              </span>
            )}
          </div>
        </div>

        {/* Upload / Replace section */}
        {(!project.r2_object_key || showReplace) && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="text-base font-semibold text-gray-900 mb-4">
              {showReplace ? 'Replace Repository' : 'Import Repository'}
            </h2>
            <ImportRepository
              projectId={id}
              mode={showReplace ? 'update' : 'add'}
              onSuccess={handleUploadSuccess}
              onCancel={showReplace ? () => setShowReplace(false) : null}
            />
          </div>
        )}

        {/* Pipeline steps */}
        {project.r2_object_key && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="text-base font-semibold text-gray-900 mb-5">Setup Pipeline</h2>

            <div className="space-y-3">
              {steps.map((step, i) => {
                const Icon = step.Icon;
                return (
                  <div
                    key={step.key}
                    className={`flex items-center justify-between p-4 rounded-xl border transition-all ${statusColor[step.status]}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                        step.status === 'completed' ? 'bg-emerald-100' :
                        step.status === 'processing' ? 'bg-blue-100' :
                        step.status === 'failed' ? 'bg-red-100' :
                        step.status === 'ready' ? 'bg-violet-100' : 'bg-gray-100'
                      }`}>
                        <Icon className={`w-4 h-4 ${
                          step.status === 'completed' ? 'text-emerald-600' :
                          step.status === 'processing' ? 'text-blue-600' :
                          step.status === 'failed' ? 'text-red-600' :
                          step.status === 'ready' ? 'text-violet-600' : 'text-gray-400'
                        }`} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-800">
                          {i + 1}. {step.label}
                        </p>
                        <p className="text-xs text-gray-500">{step.desc}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <StepStatus status={step.status} />

                      {step.key === 'parse' && step.status !== 'completed' && step.status !== 'processing' && (
                        <button
                          onClick={handleParse}
                          disabled={parsing || step.status === 'processing'}
                          className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          {parsing ? 'Starting…' : 'Parse'}
                        </button>
                      )}

                      {step.key === 'parse' && step.status === 'failed' && (
                        <button
                          onClick={handleParse}
                          disabled={parsing}
                          className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          {parsing ? 'Starting…' : 'Retry'}
                        </button>
                      )}

                      {step.key === 'analyze' && step.status === 'ready' && (
                        <Link
                          to={`/projects/${id}/analyze`}
                          className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg bg-violet-600 text-white hover:bg-violet-700 transition-colors"
                        >
                          Analyze <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectDetail;

