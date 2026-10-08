import React from 'react';
import { Compass, Waves } from 'lucide-react';

export const Header = () => {
  return (
    <header className="header-wrapper">
      <div className="brand-badge">
        <Compass className="emblem" />
        <span>Geodetic Precision System</span>
      </div>
      <h1 className="header-title">Geospatial File Measurement</h1>
      <p className="header-subtitle">
        Upload a KML or Shapefile ZIP to analyze its geometry, project CRS, and calculate high-fidelity measurements.
      </p>
      <p className="header-script-accent">
        Redolent de Géométrie et de Mesure
      </p>
    </header>
  );
};

export default Header;
