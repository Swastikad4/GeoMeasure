import React from 'react';

export const MeasurementSummary = ({ summary }) => {
  if (!summary) return null;

  const formatNumber = (num) => {
    if (num === null || num === undefined) return '0';
    return Number(num).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const areaSqKm = summary.total_polygon_area_sqm
    ? (summary.total_polygon_area_sqm / 1_000_000).toFixed(4)
    : '0';

  const lengthKm = summary.total_line_length_m
    ? (summary.total_line_length_m / 1_000).toFixed(3)
    : '0';

  return (
    <div className="metrics-section">
      <div className="metrics-header">
        <h3 className="metrics-title">Measurement Overview</h3>
        <span className="metrics-subtitle">Calculated Planar &amp; Geodesic Metrics</span>
      </div>

      <div className="metrics-grid">
        {/* Polygons Count */}
        <div className="metric-pill">
          <div className="metric-pill-title">Polygons Count</div>
          <div className="metric-pill-value">{summary.polygon_count ?? 0}</div>
          <div className="metric-pill-sub">Enclosed parcels</div>
        </div>

        {/* Total Polygon Area */}
        <div className="metric-pill">
          <div className="metric-pill-title">Total Polygon Area</div>
          <div className="metric-pill-value">
            {formatNumber(summary.total_polygon_area_sqm)}
            <span className="metric-pill-unit">m²</span>
          </div>
          <div className="metric-pill-sub">≈ {areaSqKm} km²</div>
        </div>

        {/* Lines Count */}
        <div className="metric-pill">
          <div className="metric-pill-title">Lines Count</div>
          <div className="metric-pill-value">{summary.line_count ?? 0}</div>
          <div className="metric-pill-sub">Linear corridors</div>
        </div>

        {/* Total Line Length */}
        <div className="metric-pill">
          <div className="metric-pill-title">Total Line Length</div>
          <div className="metric-pill-value">
            {formatNumber(summary.total_line_length_m)}
            <span className="metric-pill-unit">m</span>
          </div>
          <div className="metric-pill-sub">≈ {lengthKm} km</div>
        </div>

        {/* Points Count */}
        <div className="metric-pill">
          <div className="metric-pill-title">Points Count</div>
          <div className="metric-pill-value">{summary.point_count ?? 0}</div>
          <div className="metric-pill-sub">Discrete points</div>
        </div>
      </div>
    </div>
  );
};

export default MeasurementSummary;
