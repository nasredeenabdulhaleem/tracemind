import { useState, useEffect } from 'react';
import { projectsAPI } from '../services/api';

export const useProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await projectsAPI.list({ skip: 0, limit: 50 });
      setProjects(response.data.projects || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  return { projects, loading, error, reload: loadProjects };
};

export const useProject = (id) => {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadProject = async () => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await projectsAPI.get(id);
      setProject(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProject();
  }, [id]);

  return { project, loading, error, reload: loadProject };
};

// Made with Bob
