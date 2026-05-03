import { useState, useRef } from 'react';
import { toast } from 'sonner';
import { repositoryAPI } from '../../services/api';
import { UploadCloud, FileArchive, X } from 'lucide-react';

const UploadZip = ({ projectId, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const validate = (f) => {
    if (!f.name.endsWith('.zip')) { toast.error('Only ZIP files are allowed'); return false; }
    if (f.size > 100 * 1024 * 1024) { toast.error('File must be under 100MB'); return false; }
    return true;
  };

  const pickFile = (f) => { if (f && validate(f)) setFile(f); };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    pickFile(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(0);
    const toastId = toast.loading('Uploading repository…');
    try {
      await repositoryAPI.uploadZip(projectId, file, (evt) => {
        setProgress(Math.round((evt.loaded * 100) / evt.total));
      });
      toast.success('Repository uploaded successfully', { id: toastId });
      onSuccess();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed', { id: toastId });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h2 className="text-base font-semibold text-gray-900 mb-4">Upload Repository</h2>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && inputRef.current.click()}
        className={`relative flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 cursor-pointer transition-colors ${
          dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
        } ${uploading ? 'pointer-events-none opacity-60' : ''}`}
      >
        <UploadCloud className={`w-10 h-10 ${dragging ? 'text-blue-500' : 'text-gray-300'}`} />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-700">Drop your ZIP here or <span className="text-blue-600">browse</span></p>
          <p className="text-xs text-gray-400 mt-1">ZIP files only · max 100 MB</p>
        </div>
        <input ref={inputRef} type="file" accept=".zip" className="hidden" onChange={(e) => pickFile(e.target.files[0])} />
      </div>

      {/* Selected file */}
      {file && !uploading && (
        <div className="flex items-center gap-3 mt-4 p-3 bg-blue-50 rounded-xl">
          <FileArchive className="w-5 h-5 text-blue-500 shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
            <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
          <button onClick={() => setFile(null)} className="text-gray-400 hover:text-gray-600">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Progress bar */}
      {uploading && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Uploading {file?.name}</span>
            <span>{progress}%</span>
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
        className="mt-4 w-full py-2.5 text-sm font-semibold rounded-xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        {uploading ? `Uploading… ${progress}%` : 'Upload Repository'}
      </button>
    </div>
  );
};

export default UploadZip;
