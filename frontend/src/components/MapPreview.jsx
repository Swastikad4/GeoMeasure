import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Map as MapIcon } from 'lucide-react';

// Subcomponent to automatically fit bounds to the geometries
const BoundsFitter = ({ geojsonData }) => {
  const map = useMap();

  useEffect(() => {
    if (!geojsonData || !map) return;
    try {
      const geoJsonLayer = L.geoJSON(geojsonData);
      const bounds = geoJsonLayer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [30, 30], maxZoom: 16 });
      }
    } catch (e) {
      console.warn('Could not fit map bounds:', e);
    }
  }, [geojsonData, map]);

  return null;
};

export const MapPreview = ({ features, onSelectFeature }) => {
  if (!features || features.length === 0) return null;

  // Build GeoJSON FeatureCollection from features having geometry_geojson
  const validGeoFeatures = features
    .filter((f) => f.geometry_geojson)
    .map((f) => ({
      type: 'Feature',
      geometry: f.geometry_geojson,
      properties: {
        feature_id: f.feature_id,
        geometry_type: f.geometry_type,
        measurement: f.measurement,
      },
    }));

  if (validGeoFeatures.length === 0) return null;

  const featureCollection = {
    type: 'FeatureCollection',
    features: validGeoFeatures,
  };

  const geoJsonStyle = (feature) => {
    const geomType = feature?.geometry?.type;
    if (geomType === 'Polygon' || geomType === 'MultiPolygon') {
      return {
        color: '#557589', // Slate primary border
        weight: 2,
        fillColor: '#c46875', // Rosé blush fill
        fillOpacity: 0.35,
      };
    }
    // Lines
    return {
      color: '#557589',
      weight: 3.5,
      opacity: 0.85,
    };
  };

  const pointToLayer = (feature, latlng) => {
    return L.circleMarker(latlng, {
      radius: 7,
      fillColor: '#557589',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9,
    });
  };

  const onEachFeature = (feature, layer) => {
    const props = feature.properties || {};
    const meas = props.measurement || {};
    const measText = meas.value !== null && meas.value !== undefined
      ? `${Number(meas.value).toLocaleString()} ${meas.unit || ''}`
      : 'No measurement';

    const popupContent = `
      <div style="font-family: inherit; font-size: 13px; min-width: 140px;">
        <strong style="color: #192229;">Feature #${props.feature_id}</strong><br/>
        <span style="color: #557589; font-weight: 600;">${props.geometry_type}</span><br/>
        <span style="color: #c46875; font-weight: 600; margin-top: 4px; display: inline-block;">
          ${measText}
        </span>
      </div>
    `;

    layer.bindPopup(popupContent);

    layer.on({
      click: () => {
        const originalFeat = features.find((f) => f.feature_id === props.feature_id);
        if (originalFeat && onSelectFeature) {
          onSelectFeature(originalFeat);
        }
      },
    });
  };

  return (
    <div className="map-preview-container">
      <div className="map-header">
        <div style={{ display: 'flex', alignItem: 'center', gap: '0.5rem' }}>
          <MapIcon size={18} color="var(--slate-primary)" />
          <span>Interactive Geometry Map Preview</span>
        </div>
        <span style={{ fontSize: '0.8rem', color: 'var(--ink-tertiary)', fontWeight: 'normal' }}>
          {validGeoFeatures.length} plottable geometries
        </span>
      </div>

      <div className="map-element">
        <MapContainer
          center={[20, 0]}
          zoom={2}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <GeoJSON
            key={JSON.stringify(validGeoFeatures.length)}
            data={featureCollection}
            style={geoJsonStyle}
            pointToLayer={pointToLayer}
            onEachFeature={onEachFeature}
          />
          <BoundsFitter geojsonData={featureCollection} />
        </MapContainer>
      </div>
    </div>
  );
};

export default MapPreview;
