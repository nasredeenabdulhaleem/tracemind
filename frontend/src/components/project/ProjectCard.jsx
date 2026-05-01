import { Link } from 'react-router-dom';
import { useState } from 'react';
import { projectsAPI } from '../../services/api';

const ProjectCard = ({ project, onUpdate }) => {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    setDeleting(true);
    try {
      await projectsAPI.delete(project.id);
      onUpdate();
    } catch (error) {
      alert('Failed to delete project');
    } finally {
      setDeleting(false);
    }
  };

  const getStatusBadge = () => {
    if (!project.r2_object_key) {
      return <span className="badge badge-warning">No Repository</span>;
    }
    if (!project.is_indexed) {
      return <span className="badge badge-info">Not Indexed</span>;
    }
    return <span className="badge badge-success">Ready</span>;
  };

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {project.name}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2">
            {project.description || 'No description'}
          </p>
        </div>
        {getStatusBadge()}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <Link
          to={`/projects/${project.id}`}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View Details →
        </Link>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="text-sm text-red-600 hover:text-red-700"
        >
          {deleting ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    </div>
  );
};

export default ProjectCard;

// Made with Bob
