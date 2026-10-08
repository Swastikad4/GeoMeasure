import React, { useState, useMemo } from 'react';
import { Eye, Search, Filter } from 'lucide-react';

export const FeatureTable = ({ features, onSelectFeature }) => {
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFeatures = useMemo(() => {
    if (!features) return [];

    return features.filter((feat) => {
      // Type filter
      if (filterType !== 'ALL') {
        const matchesType = feat.geometry_type
          .toLowerCase()
          .includes(filterType.toLowerCase());
        if (!matchesType) return false;
      }

      // Search query in properties or ID
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const idMatches = String(feat.feature_id).includes(q);
        const typeMatches = feat.geometry_type.toLowerCase().includes(q);
        const propsMatches = Object.entries(feat.properties || {}).some(
          ([k, v]) =>
            k.toLowerCase().includes(q) || String(v).toLowerCase().includes(q)
        );
        return idMatches || typeMatches || propsMatches;
      }

      return true;
    });
  }, [features, filterType, searchQuery]);

  const formatMeasurement = (measurement) => {
    if (!measurement || measurement.value === null || measurement.value === undefined) {
      return { val: '—', unit: '—' };
    }
    return {
      val: Number(measurement.value).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }),
      unit: measurement.unit || '',
    };
  };

  const getPropertiesPreview = (properties) => {
    if (!properties || Object.keys(properties).length === 0) {
      return <span style={{ color: 'var(--ink-tertiary)' }}>No attributes</span>;
    }
    const entries = Object.entries(properties).slice(0, 2);
    const summaryStr = entries.map(([k, v]) => `${k}: ${v}`).join(' | ');
    const count = Object.keys(properties).length;
    return (
      <span title={JSON.stringify(properties, null, 2)}>
        {summaryStr} {count > 2 ? `(+${count - 2} more)` : ''}
      </span>
    );
  };

  return (
    <div className="table-card">
      <div className="table-header-bar">
        <div className="table-title-area">
          <h3>Extracted Features</h3>
        </div>

        <div className="table-filters">
          <input
            type="text"
            className="search-input"
            placeholder="Search properties or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />

          <select
            className="filter-select"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="ALL">All Geometries</option>
            <option value="POLYGON">Polygons</option>
            <option value="LINE">Lines</option>
            <option value="POINT">Points</option>
          </select>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '80px' }}>ID</th>
              <th style={{ width: '160px' }}>Geometry</th>
              <th style={{ width: '150px', textAlign: 'right' }}>Measurement</th>
              <th style={{ width: '90px' }}>Unit</th>
              <th>Properties</th>
              <th style={{ width: '100px', textAlign: 'center' }}>Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredFeatures.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--ink-tertiary)' }}>
                  No features found matching the criteria.
                </td>
              </tr>
            ) : (
              filteredFeatures.map((feat) => {
                const { val, unit } = formatMeasurement(feat.measurement);
                return (
                  <tr
                    key={feat.feature_id}
                    onClick={() => onSelectFeature(feat)}
                  >
                    <td>
                      <strong>#{feat.feature_id}</strong>
                    </td>
                    <td>
                      <span className={`geom-tag ${feat.geometry_type}`}>
                        {feat.geometry_type}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <span className={val === '—' ? 'measurement-null' : 'measurement-cell'}>
                        {val}
                      </span>
                    </td>
                    <td>{unit}</td>
                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {getPropertiesPreview(feat.properties)}
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        type="button"
                        className="btn-inspect"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectFeature(feat);
                        }}
                      >
                        <Eye size={13} style={{ marginRight: '4px', verticalAlign: '-1px' }} />
                        View
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FeatureTable;
