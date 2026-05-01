import { useState } from 'react';

const AnalysisForm = ({ onSubmit, loading }) => {
  const [bugDescription, setBugDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (bugDescription.trim()) {
      onSubmit(bugDescription);
    }
  };

  const exampleBugs = [
    'User authentication fails after password reset',
    'Payment processing returns 500 error on checkout',
    'Dashboard loads slowly with large datasets',
    'File upload fails for files larger than 10MB',
  ];

  const handleExampleClick = (example) => {
    setBugDescription(example);
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Describe the Bug</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Bug Description *
          </label>
          <textarea
            value={bugDescription}
            onChange={(e) => setBugDescription(e.target.value)}
            className="input-field"
            rows="6"
            placeholder="Describe the bug you're experiencing in detail. Include error messages, expected vs actual behavior, and steps to reproduce..."
            required
            disabled={loading}
          />
          <p className="mt-1 text-xs text-gray-500">
            Be specific about the issue, error messages, and context
          </p>
        </div>

        <button
          type="submit"
          disabled={loading || !bugDescription.trim()}
          className="w-full btn-primary"
        >
          {loading ? 'Analyzing...' : 'Analyze Bug'}
        </button>
      </form>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-sm font-medium text-gray-700 mb-3">Quick Examples:</p>
        <div className="space-y-2">
          {exampleBugs.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              disabled={loading}
              className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalysisForm;

// Made with Bob
