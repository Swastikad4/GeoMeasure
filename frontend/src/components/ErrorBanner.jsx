import React from 'react';
import { AlertCircle, AlertTriangle, X } from 'lucide-react';

export const ErrorBanner = ({ error, warning, onDismiss }) => {
  if (!error && !warning) return null;

  return (
    <>
      {error && (
        <div className="alert-banner alert-error">
          <AlertCircle size={20} style={{ flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <strong>Processing Error: </strong>
            {error}
          </div>
          {onDismiss && (
            <button
              onClick={onDismiss}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}
            >
              <X size={16} />
            </button>
          )}
        </div>
      )}

      {warning && (
        <div className="alert-banner alert-warning">
          <AlertTriangle size={20} style={{ flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <strong>Spatial Notice: </strong>
            {warning}
          </div>
        </div>
      )}
    </>
  );
};

export default ErrorBanner;
