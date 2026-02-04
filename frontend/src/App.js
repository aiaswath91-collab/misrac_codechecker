import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import '@/App.css';
import { Upload, FileCheck, Loader2, Download, AlertCircle, CheckCircle2, Clock, FileText, Activity } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analysisId, setAnalysisId] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalyses();
  }, [loadAnalyses]);

  useEffect(() => {
    if (analysisId && analysis?.status === 'running') {
      const interval = setInterval(() => {
        checkAnalysisStatus(analysisId);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [analysisId, analysis, checkAnalysisStatus]);

  const loadAnalyses = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/analyses`);
      setAnalyses(response.data);
    } catch (err) {
      console.error('Failed to load analyses:', err);
    }
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.zip')) {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please select a ZIP file');
      setSelectedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setAnalysisId(response.data.analysis_id);
      setAnalysis({ status: 'pending' });
      checkAnalysisStatus(response.data.analysis_id);
      setSelectedFile(null);
      loadAnalyses();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const checkAnalysisStatus = useCallback(async (id) => {
    try {
      const response = await axios.get(`${API}/analysis/${id}`);
      setAnalysis(response.data);

      if (response.data.status === 'completed' || response.data.status === 'failed') {
        loadAnalyses();
      }
    } catch (err) {
      console.error('Failed to check status:', err);
    }
  }, [loadAnalyses]);

  const downloadReport = async (id) => {
    try {
      const response = await axios.get(`${API}/report/${id}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `misra_report_${id}.html`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download report');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="status-icon completed" />;
      case 'running':
        return <Loader2 className="status-icon running" />;
      case 'pending':
        return <Clock className="status-icon pending" />;
      case 'failed':
        return <AlertCircle className="status-icon failed" />;
      default:
        return <Activity className="status-icon" />;
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <FileCheck size={40} className="logo-icon" />
            <div>
              <h1>MISRA C Analyzer</h1>
              <p className="subtitle">Static Analysis for Safety-Critical C Code</p>
            </div>
          </div>
          <div className="header-badge">
            <span className="badge">MISRA C:2012</span>
          </div>
        </div>
      </header>

      <div className="main-content">
        <div className="upload-section">
          <div className="upload-card">
            <div className="upload-icon-wrapper">
              <Upload size={48} className="upload-icon" />
            </div>
            <h2>Upload C/C++ Source Code</h2>
            <p className="upload-description">
              Upload a ZIP file containing your C/C++ source code for comprehensive MISRA C:2012 compliance analysis
            </p>

            <div className="file-input-wrapper">
              <input
                type="file"
                id="file-input"
                accept=".zip"
                onChange={handleFileSelect}
                disabled={uploading}
                data-testid="file-upload-input"
              />
              <label htmlFor="file-input" className="file-input-label" data-testid="file-upload-label">
                {selectedFile ? selectedFile.name : 'Choose ZIP file'}
              </label>
            </div>

            {selectedFile && (
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="upload-button"
                data-testid="upload-button"
              >
                {uploading ? (
                  <>
                    <Loader2 className="spinning" size={20} />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload size={20} />
                    Start Analysis
                  </>
                )}
              </button>
            )}

            {error && (
              <div className="error-message" data-testid="error-message">
                <AlertCircle size={20} />
                {error}
              </div>
            )}
          </div>

          {analysis && (
            <div className="status-card" data-testid="analysis-status-card">
              <div className="status-header">
                {getStatusIcon(analysis.status)}
                <div>
                  <h3>Analysis Status</h3>
                  <p className="status-text">{analysis.status.toUpperCase()}</p>
                </div>
              </div>

              {analysis.status === 'running' && (
                <div className="progress-bar">
                  <div className="progress-bar-fill"></div>
                </div>
              )}

              {analysis.status === 'completed' && (
                <div className="analysis-results" data-testid="analysis-results">
                  <div className="result-grid">
                    <div className="result-item">
                      <FileText size={24} />
                      <div>
                        <div className="result-value">{analysis.files_analyzed}</div>
                        <div className="result-label">Files Analyzed</div>
                      </div>
                    </div>
                    <div className="result-item">
                      <AlertCircle size={24} />
                      <div>
                        <div className="result-value">{analysis.total_violations}</div>
                        <div className="result-label">Total Violations</div>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => downloadReport(analysis.id)}
                    className="download-button"
                    data-testid="download-report-button"
                  >
                    <Download size={20} />
                    Download HTML Report
                  </button>
                </div>
              )}

              {analysis.status === 'failed' && (
                <div className="error-message">
                  <AlertCircle size={20} />
                  {analysis.error || 'Analysis failed'}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="analyses-section">
          <h2>Recent Analyses</h2>
          {analyses.length === 0 ? (
            <div className="empty-state">
              <FileText size={48} className="empty-icon" />
              <p>No analyses yet. Upload a ZIP file to get started.</p>
            </div>
          ) : (
            <div className="analyses-list">
              {analyses.map((item) => (
                <div key={item.id} className="analysis-item" data-testid="analysis-item">
                  <div className="analysis-item-header">
                    {getStatusIcon(item.status)}
                    <div className="analysis-item-info">
                      <div className="analysis-filename">{item.filename}</div>
                      <div className="analysis-date">{formatDate(item.created_at)}</div>
                    </div>
                  </div>
                  <div className="analysis-item-stats">
                    {item.status === 'completed' && (
                      <>
                        <span className="stat">{item.files_analyzed} files</span>
                        <span className="stat">{item.total_violations} violations</span>
                      </>
                    )}
                  </div>
                  {item.status === 'completed' && (
                    <button
                      onClick={() => downloadReport(item.id)}
                      className="download-icon-button"
                      data-testid="download-button"
                    >
                      <Download size={18} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <footer className="app-footer">
        <div className="disclaimer">
          <AlertCircle size={20} />
          <div>
            <strong>Disclaimer:</strong> This tool uses open-source static analysis engines.
            MISRA coverage is partial and non-certified. This report cannot be used for
            SIL-3/4, EN 50128, or ISO 26262 certification.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
