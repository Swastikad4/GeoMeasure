import React from 'react';
import { FileText, Layers, Globe, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export const SummaryCards = ({ fileInfo }) => {
  if (!fileInfo) return null;

  const isCompleted = fileInfo.status === 'COMPLETED';

  return (
    <div className="cards-grid">
      {/* File Card */}
      <div className="card-item">
        <div className="card-icon">
          <FileText size={20} />
        </div>
        <div className="card-content">
          <div className="card-label">File</div>
          <div className="card-value" title={fileInfo.filename}>
            {fileInfo.filename}
          </div>
          <div className="card-subtext">{fileInfo.file_type || 'Geospatial'}</div>
        </div>
      </div>

      {/* Features Count Card */}
      <div className="card-item accent-rose">
        <div className="card-icon">
          <Layers size={20} />
        </div>
        <div className="card-content">
          <div className="card-label">Features</div>
          <div className="card-value">{fileInfo.feature_count ?? 0}</div>
          <div className="card-subtext">Total Geometries</div>
        </div>
      </div>

      {/* CRS Card */}
      <div className="card-item">
        <div className="card-icon">
          <Globe size={20} />
        </div>
        <div className="card-content">
          <div className="card-label">CRS</div>
          <div className="card-value" title={fileInfo.crs || 'Unknown'}>
            {fileInfo.crs || 'Not Specified'}
          </div>
          <div className="card-subtext">
            {fileInfo.warning_message ? 'Warning: Inferred CRS' : 'Detected Spatial Reference'}
          </div>
        </div>
      </div>

      {/* Status Card */}
      <div className="card-item">
        <div className="card-icon">
          {isCompleted ? (
            <CheckCircle2 size={20} color="var(--success-text)" />
          ) : (
            <XCircle size={20} color="var(--error-text)" />
          )}
        </div>
        <div className="card-content">
          <div className="card-label">Status</div>
          <div className="card-value">
            <span
              className={`badge-status ${
                isCompleted ? 'badge-completed' : 'badge-failed'
              }`}
            >
              {fileInfo.status}
            </span>
          </div>
          <div className="card-subtext">
            {isCompleted ? 'Processed Successfully' : 'Processing Encountered Issues'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryCards;
