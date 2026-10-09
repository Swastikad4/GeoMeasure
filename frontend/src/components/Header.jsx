import React from 'react';

export const Header = () => {
  return (
    <header className="header-wrapper">
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
