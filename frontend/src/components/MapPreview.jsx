import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Map as MapIcon } from 'lucide-react';

// Bounding box for India geographic extent
const INDIA_BOUNDS = [
  [6.0, 68.0],   // Southwest coordinates [lat, lng]
  [37.5, 97.5],  // Northeast coordinates [lat, lng]
];

// Helper to recursively shift GeoJSON coordinates
const shiftCoords = (coords, dLng, dLat) => {
  if (typeof coords[0] === 'number') {
    return [coords[0] + dLng, coords[1] + dLat];
  }
  return coords.map((c) => shiftCoords(c, dLng, dLat));
};

// Subcomponent to automatically fit bounds to the geometries within India
const BoundsFitter = ({ geojsonData }) => {
  const map = useMap();

  useEffect(() => {
    if (!geojsonData || !map) return;
    try {
      const geoJsonLayer = L.geoJSON(geojsonData);
      const bounds = geoJsonLayer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
      } else {
        map.setView([20.5937, 78.9629], 5);
      }
    } catch (e) {
      console.warn('Could not fit map bounds:', e);
      map.setView([20.5937, 78.9629], 5);
    }
  }, [geojsonData, map]);

  return null;
};

export const MapPreview = ({ features, onSelectFeature }) => {
  if (!features || features.length === 0) return null;

  // Process features to ensure strict India orientation
  const { featureCollection, isReanchored, validCount } = useMemo(() => {
    const valid = features
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

    if (valid.length === 0) {
      return { featureCollection: null, isReanchored: false, validCount: 0 };
    }

    // 1. Scan coordinates to determine if geometries lie within India bounds
    let minLng = Infinity, maxLng = -Infinity, minLat = Infinity, maxLat = -Infinity;

    const scan = (coords) => {
      if (typeof coords[0] === 'number') {
        const [lng, lat] = coords;
        if (lng < minLng) minLng = lng;
        if (lng > maxLng) maxLng = lng;
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
      } else {
        coords.forEach(scan);
      }
    };

    valid.forEach((f) => {
      if (f.geometry?.coordinates) {
        scan(f.geometry.coordinates);
      }
    });

    const isInsideIndia = (
      minLng >= 67.0 && maxLng <= 98.5 && minLat >= 6.0 && maxLat <= 38.0
    );

    // 2. If outside India (e.g. New York, Europe), re-anchor to India (New Delhi Central Vista grid)
    let processedFeatures = valid;
    let reanchored = false;

    if (!isInsideIndia && minLng !== Infinity) {
      reanchored = true;
      const centerLng = (minLng + maxLng) / 2;
      const centerLat = (minLat + maxLat) / 2;

      // Anchor to New Delhi, India
      const targetLng = 77.215;
      const targetLat = 28.615;

      const dLng = targetLng - centerLng;
      const dLat = targetLat - centerLat;

      processedFeatures = valid.map((f) => ({
        ...f,
        geometry: {
          ...f.geometry,
          coordinates: shiftCoords(f.geometry.coordinates, dLng, dLat),
        },
      }));
    }

    return {
      featureCollection: {
        type: 'FeatureCollection',
        features: processedFeatures,
      },
      isReanchored: reanchored,
      validCount: valid.length,
    };
  }, [features]);

  if (!featureCollection) return null;

  const geoJsonStyle = (feature) => {
    const geomType = feature?.geometry?.type;
    if (geomType === 'Polygon' || geomType === 'MultiPolygon') {
      return {
        color: '#557589',
        weight: 2,
        fillColor: '#c46875',
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <MapIcon size={16} color="var(--slate-primary)" />
          <span>Interactive Geometry Map Preview (India)</span>
          {isReanchored && (
            <span className="india-badge">
              🇮🇳 India-Oriented View (Re-anchored to India Grid)
            </span>
          )}
        </div>
        <span style={{ fontSize: '0.78rem', color: 'var(--ink-tertiary)', fontWeight: 'normal' }}>
          {validCount} plottable geometries
        </span>
      </div>

      <div className="map-element">
        <MapContainer
          center={[20.5937, 78.9629]}
          zoom={5}
          minZoom={4}
          maxBounds={INDIA_BOUNDS}
          maxBoundsViscosity={1.0}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <GeoJSON
            key={JSON.stringify(features.length) + (isReanchored ? '-reanchored' : '-native')}
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
