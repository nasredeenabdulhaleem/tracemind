/**
 * ImportRepository — handles both GitHub clone and ZIP upload.
 * Used in CreateProjectModal (new project) and ProjectDetail (update/replace).
 *
 * Props:
 *   projectId   – UUID of the already-created project
 *   mode        – 'add' | 'update' (shows warning banner in update mode)
 *   initialView – 'pick' | 'github' | 'zip'
 *   onSuccess   – called after successful import
 *   onCancel    – called when user cancels / backs out of the whole component
 */
import { useState, useRef } from 'react';
import { toast } from 'sonner';
import { repositoryAPI } from '../../services/api';
import {
  Github, UploadCloud, FileArchive, X,
  ArrowLeft, Loader2, AlertTriangle,
} from 'lucide-react';

const ImportRepository = ({
  projectId,
  mode = 'add',
  initialView = 'pick',
  onSuccess,
  onCancel,
}) => {
  const [view, setView] = useState(initialView);

  // GitHub state
  const [githubUrl, setGithubUrl] = useState('');
  const [githubLoading, setGithubLoading] = useState(false);
  const [githubError, setGithubError] = useState('');

  // ZIP state
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef();

  const isUpdate = mode === 'update';

  // ── GitHub ────────────────────────────────────────────────────────────────

  const validateGithubUrl = (url) => {
    if (!url.trim()) return 'Please enter a GitHub URL';
    const valid = [
      'https://github.com/',
      'http://github.com/',
      'git@github.com:',
      'github.com/',
    ];
    if (!valid.some((p) => url.includes(p))) {
      return 'Must be a valid GitHub URL (e.g. https://github.com/owner/repo)';
    }
    return null;
  };

  const handleGithubConnect = async () => {
    const err = validateGithubUrl(githubUrl);
    if (err) { setGithubError(err); return; }
    setGithubError('');
    setGithubLoading(true);
    const toastId = toast.loading('Cloning repository…');
    try {
      await repositoryAPI.connectGithub(projectId, githubUrl.trim());
      toast.success('Repository cloned and uploaded', { id: toastId });
      onSuccess();
    } catch (e) {
      const msg = e.response?.data?.detail || 'Failed to connect repository';
      setGithubError(msg);
      toast.error(msg, { id: toastId });
    } finally {
      setGithubLoading(false);
    }
  };

  // ── ZIP ───────────────────────────────────────────────────────────────────

  const validateFile = (f) => {
    if (!f.name.toLowerCase().endsWith('.zip')) {
      toast.error('Only ZIP files are allowed');
      return false;
    }
    if (f.size > 100 * 1024 * 1024) {
      toast.error('File must be under 100 MB');
      return false;
    }
    return true;
  };

  const pickFile = (f) => { if (f && validateFile(f)) setFile(f); };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(0);
    const toastId = toast.loading('Uploading repository…');
    try {
      await repositoryAPI.uploadZip(projectId, file, (evt) => {
        if (evt.total) setProgress(Math.round((evt.loaded * 100) / evt.total));
      });
      toast.success('Repository uploaded successfully', { id: toastId });
      onSuccess();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Upload failed', { id: toastId });
    } finally {
      setUploading(false);
    }
  };

  // ── Update warning banner ─────────────────────────────────────────────────

  const UpdateWarning = () => isUpdate ? (
    <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-700 mb-4">
      <AlertTriangle size={13} className="shrink-0 mt-0.5" />
      <span>
        Replacing the repository will <strong>reset parsing and indexing</strong>.
        You'll need to re-run those steps after the new code is uploaded.
      </span>
    </div>
  ) : null;

  // ── Source picker ─────────────────────────────────────────────────────────

  if (view === 'pick') {
    return (
      <div className="space-y-4">
        <UpdateWarning />

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setView('github')}
            className="flex flex-col items-center gap-3 p-5 rounded-xl border-2 border-gray-200 hover:border-gray-900 hover:bg-gray-50 transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-gray-900 flex items-center justify-center group-hover:scale-105 transition-transform">
              <Github className="w-5 h-5 text-white" />
            </div>
            <div className="text-center">
              <p className="text-sm font-semibold text-gray-800">GitHub</p>
              <p className="text-xs text-gray-400 mt-0.5">Clone from URL</p>
            </div>
          </button>

          <button
            onClick={() => setView('zip')}
            className="flex flex-col items-center gap-3 p-5 rounded-xl border-2 border-gray-200 hover:border-orange-400 hover:bg-orange-50 transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center group-hover:scale-105 transition-transform">
              <UploadCloud className="w-5 h-5 text-orange-600" />
            </div>
            <div className="text-center">
              <p className="text-sm font-semibold text-gray-800">ZIP Upload</p>
              <p className="text-xs text-gray-400 mt-0.5">Upload archive</p>
            </div>
          </button>
        </div>

        {onCancel && (
          <button
            onClick={onCancel}
            className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowLeft size={14} /> Cancel
          </button>
        )}
      </div>
    );
  }

  // ── GitHub view ───────────────────────────────────────────────────────────

  if (view === 'github') {
    return (
      <div className="space-y-4">
        <button
          onClick={() => { setView('pick'); setGithubError(''); setGithubUrl(''); }}
          className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition-colors"
        >
          <ArrowLeft size={14} /> Back
        </button>

        <UpdateWarning />

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center shrink-0">
            <Github className="w-4 h-4 text-white" />
          </div>
          <h3 className="text-sm font-semibold text-gray-900">Connect GitHub Repository</h3>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">
            Repository URL
          </label>
          <input
            type="url"
            value={githubUrl}
            onChange={(e) => { setGithubUrl(e.target.value); setGithubError(''); }}
            onKeyDown={(e) => { if (e.key === 'Enter') handleGithubConnect(); }}
            placeholder="https://github.com/owner/repository"
            disabled={githubLoading}
            className={`w-full border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 transition-colors
              ${githubError ? 'border-red-300 bg-red-50' : 'border-gray-200'}
              ${githubLoading ? 'opacity-60 cursor-not-allowed' : ''}
            `}
          />
          {githubError && (
            <p className="text-xs text-red-500 mt-1">{githubError}</p>
          )}
          <p className="text-xs text-gray-400 mt-1.5">
            Public repositories only · shallow clone for speed
          </p>
        </div>

        {githubLoading && (
          <div className="flex items-center gap-3 bg-blue-50 border border-blue-100 rounded-xl p-3">
            <Loader2 size={14} className="animate-spin text-blue-500 shrink-0" />
            <div className="text-xs text-blue-800">
              <p className="font-medium">Cloning repository…</p>
              <p className="text-blue-500 mt-0.5">This may take 30–60 seconds</p>
            </div>
          </div>
        )}

        <button
          onClick={handleGithubConnect}
          disabled={!githubUrl.trim() || githubLoading}
          className="w-full py-2.5 bg-gray-900 text-white text-sm font-semibold rounded-xl hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {githubLoading
            ? <><Loader2 size={14} className="animate-spin" /> Cloning…</>
            : <><Github size={14} /> Clone &amp; Import</>
          }
        </button>
      </div>
    );
  }

  // ── ZIP view ──────────────────────────────────────────────────────────────

  if (view === 'zip') {
    return (
      <div className="space-y-4">
        <button
          onClick={() => { setView('pick'); setFile(null); }}
          className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition-colors"
        >
          <ArrowLeft size={14} /> Back
        </button>

        <UpdateWarning />

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center shrink-0">
            <FileArchive className="w-4 h-4 text-orange-600" />
          </div>
          <h3 className="text-sm font-semibold text-gray-900">Upload ZIP Archive</h3>
        </div>

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            pickFile(e.dataTransfer.files[0]);
          }}
          onClick={() => !uploading && fileInputRef.current?.click()}
          className={`flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-8 cursor-pointer select-none transition-colors
            ${dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'}
            ${uploading ? 'pointer-events-none opacity-60' : ''}
          `}
        >
          <UploadCloud className={`w-8 h-8 ${dragging ? 'text-blue-500' : 'text-gray-300'}`} />
          <p className="text-sm text-gray-600">
            Drop ZIP here or <span className="text-blue-600 font-medium">browse</span>
          </p>
          <p className="text-xs text-gray-400">ZIP files only · max 100 MB</p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            className="hidden"
            onChange={(e) => pickFile(e.target.files[0])}
          />
        </div>

        {/* Selected file preview */}
        {file && !uploading && (
          <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-100 rounded-xl">
            <FileArchive className="w-5 h-5 text-blue-500 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button
              onClick={() => setFile(null)}
              className="text-gray-400 hover:text-red-500 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Upload progress */}
        {uploading && (
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-gray-500">
              <span className="truncate max-w-[200px]">Uploading {file?.name}</span>
              <span className="shrink-0 ml-2">{progress}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {uploading
            ? <><Loader2 size={14} className="animate-spin" /> Uploading… {progress}%</>
            : <><UploadCloud size={14} /> Upload Repository</>
          }
        </button>
      </div>
    );
  }

  return null;
};

export default ImportRepository;
