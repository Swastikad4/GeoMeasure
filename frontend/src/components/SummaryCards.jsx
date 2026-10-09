import React from 'react';
import { FileText, Layers, Globe, CheckCircle2, XCircle } from 'lucide-react';

export const SummaryCards = ({ fileInfo }) => {
  if (!fileInfo) return null;

  const isCompleted = fileInfo.status === 'COMPLETED';

  return (
    <div className="cards-grid">
      {/* 1. File Metric */}
      <div className="card-item">
        <div className="card-header-row">
          <span className="card-label">File</span>
          <FileText size={15} className="card-outline-icon" />
        </div>
        <div className="card-value" title={fileInfo.filename}>
          {fileInfo.filename}
        </div>
        <div className="card-subtext">{fileInfo.file_type || 'Geospatial'}</div>
      </div>

      {/* 2. Features Metric */}
      <div className="card-item">
        <div className="card-header-row">
          <span className="card-label">Features</span>
          <Layers size={15} className="card-outline-icon" />
        </div>
        <div className="card-value">
          {fileInfo.feature_count ?? 0}
        </div>
        <div className="card-subtext">Total Geometries</div>
      </div>

      {/* 3. CRS Metric */}
      <div className="card-item">
        <div className="card-header-row">
          <span className="card-label">CRS</span>
          <Globe size={15} className="card-outline-icon" />
        </div>
        <div className="card-value" title={fileInfo.crs || 'Unknown'}>
          {fileInfo.crs || 'Not Specified'}
        </div>
        <div className="card-subtext">
          {fileInfo.warning_message ? 'Warning: Inferred CRS' : 'Detected Spatial Reference'}
        </div>
      </div>

      {/* 4. Status Metric */}
      <div className="card-item">
        <div className="card-header-row">
          <span className="card-label">Status</span>
          {isCompleted ? (
            <CheckCircle2 size={15} className="card-outline-icon status-icon-success" />
          ) : (
            <XCircle size={15} className="card-outline-icon status-icon-error" />
          )}
        </div>
        <div className="card-value card-status-value">
          <span className={`status-pill ${isCompleted ? 'status-pill-success' : 'status-pill-error'}`}>
            <span className={`status-dot ${isCompleted ? 'status-dot-success' : 'status-dot-error'}`} />
            {fileInfo.status}
          </span>
        </div>
        <div className="card-subtext">
          {isCompleted ? 'Processed Successfully' : 'Processing Encountered Issues'}
        </div>
      </div>
    </div>
  );
};

export default SummaryCards;
