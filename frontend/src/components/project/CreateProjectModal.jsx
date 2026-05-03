import { useState } from 'react';
import { toast } from 'sonner';
import { projectsAPI } from '../../services/api';
import ImportRepository from './ImportRepository';
import { X, FolderPlus, CheckCircle2, Loader2, Github, UploadCloud } from 'lucide-react';

const SOURCE_OPTIONS = [
  {
    value: 'github',
    Icon: Github,
    label: 'GitHub',
    desc: 'Clone a public GitHub repository',
    iconBg: 'bg-gray-900',
    iconColor: 'text-white',
    border: 'hover:border-gray-900',
  },
  {
    value: 'zip',
    Icon: UploadCloud,
    label: 'ZIP Upload',
    desc: 'Upload a ZIP archive',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600',
    border: 'hover:border-orange-400',
  },
];

const STEPS = [
  { key: 'details', label: 'Details' },
  { key: 'import',  label: 'Import'  },
  { key: 'done',    label: 'Done'    },
];

const CreateProjectModal = ({ onClose, onSuccess }) => {
  const [step, setStep]           = useState('details');
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState('');
  const [projectId, setProjectId] = useState(null);
  const [formData, setFormData]   = useState({
    name: '',
    description: '',
    repo_type: 'github',
  });

  const stepIndex = STEPS.findIndex((s) => s.key === step);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return;
    setError('');
    setLoading(true);
    try {
      const response = await projectsAPI.create({
        name: formData.name.trim(),
        description: formData.description.trim(),
        repo_type: formData.repo_type,
      });
      setProjectId(response.data.id);
      setStep('import');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const handleImportSuccess = () => {
    setStep('done');
    setTimeout(() => onSuccess(projectId), 400);
  };

  const handleSkip = () => {
    onSuccess(projectId);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-xl overflow-hidden">

        {/* ── Header ── */}
        <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
              <FolderPlus className="w-4 h-4 text-blue-600" />
            </div>
            <h2 className="text-base font-semibold text-gray-900">
              {step === 'details' ? 'New Project' : step === 'import' ? 'Import Code' : 'All Set!'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100"
          >
            <X size={16} />
          </button>
        </div>

        {/* ── Step progress ── */}
        <div className="flex items-center gap-0 px-6 py-3 bg-gray-50 border-b border-gray-100">
          {STEPS.map((s, i) => (
            <div key={s.key} className="flex items-center gap-0 flex-1">
              <div className={`flex items-center gap-1.5 text-xs font-medium transition-colors
                ${i < stepIndex ? 'text-emerald-600' : i === stepIndex ? 'text-blue-600' : 'text-gray-400'}`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0
                  ${i < stepIndex ? 'bg-emerald-100' : i === stepIndex ? 'bg-blue-100' : 'bg-gray-100'}`}
                >
                  {i < stepIndex
                    ? <CheckCircle2 size={12} className="text-emerald-600" />
                    : <span className="text-xs">{i + 1}</span>
                  }
                </div>
                <span className="hidden sm:inline">{s.label}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-px mx-2 ${i < stepIndex ? 'bg-emerald-200' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        {/* ── Body ── */}
        <div className="px-6 py-5">

          {/* STEP 1: Details */}
          {step === 'details' && (
            <form onSubmit={handleCreateProject} className="space-y-4">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Project Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                  placeholder="My Awesome Project"
                  required
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Description <span className="text-gray-400 font-normal">(optional)</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors resize-none"
                  rows={2}
                  placeholder="Brief description of your project…"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-2">
                  Code Source
                </label>
                <div className="grid grid-cols-2 gap-2.5">
                  {SOURCE_OPTIONS.map(({ value, Icon, label, desc, iconBg, iconColor, border }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setFormData({ ...formData, repo_type: value })}
                      className={`flex items-center gap-3 p-3 rounded-xl border-2 text-left transition-all
                        ${formData.repo_type === value
                          ? 'border-blue-500 bg-blue-50'
                          : `border-gray-200 ${border} hover:bg-gray-50`
                        }`}
                    >
                      <div className={`w-8 h-8 rounded-lg ${iconBg} flex items-center justify-center shrink-0`}>
                        <Icon size={15} className={iconColor} />
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-gray-800">{label}</p>
                        <p className="text-xs text-gray-400 leading-tight">{desc}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || !formData.name.trim()}
                className="w-full py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 mt-2"
              >
                {loading
                  ? <><Loader2 size={14} className="animate-spin" /> Creating…</>
                  : 'Create Project & Import Code →'
                }
              </button>
            </form>
          )}

          {/* STEP 2: Import */}
          {step === 'import' && projectId && (
            <div className="space-y-5">
              <ImportRepository
                projectId={projectId}
                mode="add"
                initialView={formData.repo_type}
                onSuccess={handleImportSuccess}
                onCancel={null}
              />
              <div className="pt-1 border-t border-gray-100 text-center">
                <button
                  onClick={handleSkip}
                  className="text-xs text-gray-400 hover:text-gray-600 transition-colors py-1"
                >
                  Skip for now — I'll import from the project page
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Done */}
          {step === 'done' && (
            <div className="flex flex-col items-center py-6 gap-3 text-center">
              <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center">
                <CheckCircle2 className="w-7 h-7 text-emerald-600" />
              </div>
              <p className="text-base font-semibold text-gray-900">Project ready!</p>
              <p className="text-sm text-gray-500">Repository imported. Taking you there…</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateProjectModal;

