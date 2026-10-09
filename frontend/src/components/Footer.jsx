import React from 'react';
import { Compass, ExternalLink } from 'lucide-react';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="simple-footer">
      <div className="footer-container">
        <div className="footer-brand">
          <div className="footer-brand-header">
            <Compass className="footer-brand-icon" />
            <span className="footer-brand-name">GeoMeasure</span>
          </div>
          <p className="footer-brand-tagline">
            Geodetic precision system for metric polygon area &amp; geodesic line measurements.
          </p>
        </div>

        <div className="footer-meta">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-doc-link"
          >
            <span>API Docs (Swagger)</span>
            <ExternalLink className="footer-link-icon" />
          </a>
          <span className="footer-version-tag">v1.0.0</span>
        </div>
      </div>

      <div className="footer-bottom">
        <p className="footer-copy">
          &copy; {currentYear} GeoMeasure &bull; Built with FastAPI, GeoPandas &amp; React
        </p>
      </div>
    </footer>
  );
};

export default Footer;
