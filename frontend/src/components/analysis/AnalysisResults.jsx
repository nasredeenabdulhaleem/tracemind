import { useState } from 'react';

const AnalysisResults = ({ analysis }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'rootcause', label: 'Root Cause' },
    { id: 'fix', label: 'Suggested Fix' },
    { id: 'test', label: 'Test Code' },
  ];

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Analysis Results</h2>
        <span className="text-xs text-gray-500">
          {analysis.processing_time_ms}ms
        </span>
      </div>

      <div className="border-b border-gray-200 mb-4">
        <nav className="flex space-x-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="space-y-4">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Bug Description</h3>
              <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                {analysis.bug_description}
              </p>
            </div>

            {analysis.affected_files && analysis.affected_files.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Affected Files</h3>
                <div className="space-y-1">
                  {analysis.affected_files.map((file, index) => (
                    <div key={index} className="text-sm text-gray-600 bg-gray-50 p-2 rounded font-mono">
                      {file}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Simple Explanation</h3>
              <p className="text-sm text-gray-600 whitespace-pre-wrap">
                {analysis.explanation_simple}
              </p>
            </div>
          </div>
        )}

        {activeTab === 'rootcause' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Root Cause Analysis</h3>
              <p className="text-sm text-gray-600 whitespace-pre-wrap">
                {analysis.root_cause}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Technical Explanation</h3>
              <p className="text-sm text-gray-600 whitespace-pre-wrap">
                {analysis.explanation_technical}
              </p>
            </div>
          </div>
        )}

        {activeTab === 'fix' && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Suggested Fix</h3>
            <pre className="text-xs bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
              <code>{analysis.suggested_fix}</code>
            </pre>
          </div>
        )}

        {activeTab === 'test' && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Generated Test Code</h3>
            {analysis.generated_test ? (
              <pre className="text-xs bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                <code>{analysis.generated_test}</code>
              </pre>
            ) : (
              <p className="text-sm text-gray-500 italic">No test code generated</p>
            )}
          </div>
        )}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Analysis ID: {analysis.id} • Created: {new Date(analysis.created_at).toLocaleString()}
        </p>
      </div>
    </div>
  );
};

export default AnalysisResults;

// Made with Bob
