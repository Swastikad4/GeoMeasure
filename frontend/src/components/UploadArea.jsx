import React, { useState, useRef } from 'react';
import { UploadCloud, FileCode, CheckCircle, X, ArrowRight, Loader2 } from 'lucide-react';

export const UploadArea = ({ onFileSelect, onAnalyze, selectedFile, isProcessing, onClearFile, onSelectSample }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="upload-card">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInput}
        accept=".kml,.zip"
        style={{ display: 'none' }}
        id="geospatial-file-input"
      />

      <div
        className={`dropzone ${isDragging ? 'active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isProcessing && fileInputRef.current?.click()}
      >
        <div className="dropzone-icon-wrap">
          <UploadCloud size={28} />
        </div>
        <h2 className="dropzone-title">Click to upload or drag & drop</h2>
        <p className="dropzone-formats">Supported formats: .KML, .ZIP (Shapefile)</p>
      </div>

      {selectedFile && (
        <div className="selected-file-banner">
          <div className="selected-file-info">
            <FileCode size={20} color="var(--slate-primary)" />
            <div>
              <div className="selected-file-name">{selectedFile.name}</div>
              <div className="selected-file-size">{formatFileSize(selectedFile.size)}</div>
            </div>
          </div>
          {!isProcessing && (
            <button
              className="remove-btn"
              onClick={onClearFile}
              title="Remove file"
              type="button"
            >
              <X size={18} />
            </button>
          )}
        </div>
      )}

      {isProcessing && (
        <div className="processing-indicator">
          <div className="spinner" />
          <span>Processing geospatial file...</span>
        </div>
      )}

      <div className="upload-actions">
        <div className="sample-buttons">
          <span className="sample-label">Quick Test:</span>
          <button
            type="button"
            className="btn-sample"
            disabled={isProcessing}
            onClick={() => onSelectSample('sample_polygon.kml')}
          >
            Sample KML
          </button>
          <button
            type="button"
            className="btn-sample"
            disabled={isProcessing}
            onClick={() => onSelectSample('sample_routes.kml')}
          >
            Routes & Points KML
          </button>
          <button
            type="button"
            className="btn-sample"
            disabled={isProcessing}
            onClick={() => onSelectSample('sample_shapefile.zip')}
          >
            Shapefile ZIP
          </button>
        </div>

        <button
          type="button"
          id="btn-analyze-file"
          className="btn-primary"
          disabled={!selectedFile || isProcessing}
          onClick={onAnalyze}
        >
          {isProcessing ? (
            <>
              <Loader2 size={18} className="spinner" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <span>Analyze File</span>
              <ArrowRight size={16} />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default UploadArea;
