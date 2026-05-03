import { Link } from 'react-router-dom';
import { useState } from 'react';
import { toast } from 'sonner';
import { projectsAPI } from '../../services/api';
import {
  FolderOpen, Trash2, ArrowRight, CheckCircle2, Clock,
  Zap, AlertCircle, Github, FileArchive, Loader2,
} from 'lucide-react';

const ProjectCard = ({ project, onUpdate }) => {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`Delete "${project.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    const toastId = toast.loading('Deleting project…');
    try {
      await projectsAPI.delete(project.id);
      toast.success('Project deleted', { id: toastId });
      onUpdate();
    } catch {
      toast.error('Failed to delete project', { id: toastId });
    } finally {
      setDeleting(false);
    }
  };

  const getStatus = () => {
    if (!project.r2_object_key)
      return { label: 'No Code', color: 'bg-gray-100 text-gray-500', Icon: Clock };
    if (project.indexing_status === 'processing')
      return { label: 'Processing', color: 'bg-blue-100 text-blue-700', Icon: Loader2, spin: true };
    if (project.is_indexed)
      return { label: 'Ready', color: 'bg-emerald-100 text-emerald-700', Icon: Zap };
    if (project.indexing_status === 'failed')
      return { label: 'Error', color: 'bg-red-100 text-red-700', Icon: AlertCircle };
    return { label: 'Uploaded', color: 'bg-blue-100 text-blue-700', Icon: CheckCircle2 };
  };

  const { label, color, Icon, spin } = getStatus();

  const repoSource = project.repo_type === 'github'
    ? { Icon: Github, text: project.repo_url?.replace('https://github.com/', '') || 'GitHub' }
    : project.repo_type === 'zip'
    ? { Icon: FileArchive, text: 'ZIP Upload' }
    : null;

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center shrink-0">
          <FolderOpen className="w-5 h-5 text-blue-500" />
        </div>
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${color}`}>
          <Icon className={`w-3 h-3 ${spin ? 'animate-spin' : ''}`} />
          {label}
        </span>
      </div>

      <div className="flex-1">
        <h3 className="text-base font-semibold text-gray-900 leading-snug">{project.name}</h3>
        <p className="text-sm text-gray-500 mt-1 line-clamp-2">
          {project.description || 'No description provided'}
        </p>

        {/* Repo source badge */}
        {repoSource && (
          <div className="flex items-center gap-1 mt-2">
            <repoSource.Icon className="w-3 h-3 text-gray-400" />
            <span className="text-xs text-gray-400 truncate max-w-[180px]">{repoSource.text}</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <Link
          to={`/projects/${project.id}`}
          className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
        >
          Open <ArrowRight className="w-3.5 h-3.5" />
        </Link>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-red-500 disabled:opacity-50 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          {deleting ? 'Deleting…' : 'Delete'}
        </button>
      </div>
    </div>
  );
};

export default ProjectCard;

