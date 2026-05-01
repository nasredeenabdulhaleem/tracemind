import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { projectsAPI, repositoryAPI, parsingAPI, indexingAPI } from '../services/api';
import Navbar from '../components/common/Navbar';
import UploadZip from '../components/project/UploadZip';

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadProject();
  }, [id]);

  const loadProject = async () => {
    try {
      const response = await projectsAPI.get(id);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to load project:', error);
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    loadProject();
  };

  const handleParse = async () => {
    setProcessing(true);
    try {
      await parsingAPI.parse(id);
      alert('Parsing started! This may take a few minutes.');
      setTimeout(loadProject, 2000);
    } catch (error) {
      alert('Failed to start parsing');
    } finally {
      setProcessing(false);
    }
  };

  const handleIndex = async () => {
    setProcessing(true);
    try {
      await indexingAPI.createIndex(id);
      alert('Indexing started! This may take a few minutes.');
      setTimeout(loadProject, 2000);
    } catch (error) {
      alert('Failed to start indexing');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link to="/" className="text-blue-600 hover:text-blue-700 text-sm">
            ← Back to Projects
          </Link>
        </div>

        <div className="card mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{project.name}</h1>
          <p className="text-gray-600 mb-4">{project.description || 'No description'}</p>
          
          <div className="flex space-x-4">
            {project.r2_object_key && (
              <span className="badge badge-success">Repository Uploaded</span>
            )}
            {project.is_indexed && (
              <span className="badge badge-success">Indexed</span>
            )}
          </div>
        </div>

        {!project.r2_object_key ? (
          <UploadZip projectId={id} onSuccess={handleUploadSuccess} />
        ) : (
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-lg font-semibold mb-4">Processing Steps</h2>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <p className="font-medium">1. Parse Code</p>
                    <p className="text-sm text-gray-600">Extract code chunks and definitions</p>
                  </div>
                  <button
                    onClick={handleParse}
                    disabled={processing}
                    className="btn-primary text-sm"
                  >
                    Parse
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <p className="font-medium">2. Create Index</p>
                    <p className="text-sm text-gray-600">Build vector embeddings for search</p>
                  </div>
                  <button
                    onClick={handleIndex}
                    disabled={processing || !project.r2_object_key}
                    className="btn-primary text-sm"
                  >
                    Index
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <p className="font-medium">3. Analyze Bugs</p>
                    <p className="text-sm text-gray-600">Use AI to find and fix bugs</p>
                  </div>
                  <Link
                    to={`/projects/${id}/analyze`}
                    className={`btn-primary text-sm ${!project.is_indexed ? 'opacity-50 pointer-events-none' : ''}`}
                  >
                    Analyze
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectDetail;

// Made with Bob
