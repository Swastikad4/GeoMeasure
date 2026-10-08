import React from 'react';
import { X, Check } from 'lucide-react';

export const FeatureModal = ({ feature, crs, onClose }) => {
  if (!feature) return null;

  const measurement = feature.measurement || {};
  const hasMeasurement = measurement.value !== null && measurement.value !== undefined;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Feature #{feature.feature_id} Details</h3>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="detail-row">
            <span className="detail-label">Feature ID</span>
            <span className="detail-value">#{feature.feature_id}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Geometry Type</span>
            <span className="detail-value">
              <span className={`geom-tag ${feature.geometry_type}`}>
                {feature.geometry_type}
              </span>
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Measurement</span>
            <span className="detail-value">
              {hasMeasurement ? (
                <>
                  {Number(measurement.value).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}{' '}
                  <strong>{measurement.unit}</strong>{' '}
                  <span style={{ fontSize: '0.8rem', color: 'var(--ink-tertiary)' }}>
                    ({measurement.type})
                  </span>
                </>
              ) : (
                <span style={{ color: 'var(--ink-tertiary)' }}>
                  {measurement.message || 'No measurement applicable'}
                </span>
              )}
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">CRS (Reference)</span>
            <span className="detail-value">{crs || 'Not Specified'}</span>
          </div>

          {/* Properties Attributes */}
          <div className="properties-list">
            <div className="properties-title">Properties & Attributes</div>
            <div className="property-box">
              {Object.keys(feature.properties || {}).length === 0 ? (
                <div style={{ color: 'var(--ink-tertiary)', fontSize: '0.85rem' }}>
                  No additional attribute metadata.
                </div>
              ) : (
                Object.entries(feature.properties).map(([key, val]) => (
                  <div key={key} className="prop-kv">
                    <span className="prop-k">{key}</span>
                    <span className="prop-v">{String(val)}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeatureModal;
