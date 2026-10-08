import React, { useState } from 'react';
import Header from './components/Header';
import UploadArea from './components/UploadArea';
import SummaryCards from './components/SummaryCards';
import MeasurementSummary from './components/MeasurementSummary';
import FeatureTable from './components/FeatureTable';
import FeatureModal from './components/FeatureModal';
import MapPreview from './components/MapPreview';
import ErrorBanner from './components/ErrorBanner';
import { uploadFile, getFeatures, fetchSampleFile } from './services/api';

export function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fileInfo, setFileInfo] = useState(null);
  const [features, setFeatures] = useState([]);
  const [activeModalFeature, setActiveModalFeature] = useState(null);
  const [error, setError] = useState(null);
  const [warning, setWarning] = useState(null);

  const handleFileSelect = (file) => {
    setError(null);
    setWarning(null);

    // Basic client check
    const validExts = ['.kml', '.zip'];
    const fileName = file.name.toLowerCase();
    const isValid = validExts.some((ext) => fileName.endsWith(ext));

    if (!isValid) {
      setError('Please upload a .kml file or a .zip containing a Shapefile.');
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  const handleSelectSample = async (sampleFilename) => {
    try {
      setError(null);
      setWarning(null);
      setIsProcessing(true);
      const sampleFile = await fetchSampleFile(sampleFilename);
      setSelectedFile(sampleFile);
      // Auto-trigger analysis for seamless preview
      await executeAnalysis(sampleFile);
    } catch (err) {
      console.error('Failed to load sample:', err);
      setError('Could not load sample file. Please upload a file manually.');
    } finally {
      setIsProcessing(false);
    }
  };

  const executeAnalysis = async (fileToUpload) => {
    if (!fileToUpload) return;

    setIsProcessing(true);
    setError(null);
    setWarning(null);

    try {
      // 1. Upload & process file
      const uploadResult = await uploadFile(fileToUpload);

      if (uploadResult.success && uploadResult.data) {
        const data = uploadResult.data;
        setFileInfo(data);
        if (data.warning_message) {
          setWarning(data.warning_message);
        }

        // 2. Fetch full feature collection with measurements & geometry
        const featuresResult = await getFeatures(data.id);
        if (featuresResult.success && featuresResult.data) {
          setFeatures(featuresResult.data.features || []);
        }
      } else {
        setError(uploadResult.message || "We couldn't process this file. Please check that the file is valid and try again.");
      }
    } catch (err) {
      console.error('Analysis error:', err);
      let errMsg = "We couldn't process this file. Please check that the file is valid and try again.";
      if (err.response?.data?.message) {
        errMsg = err.response.data.message;
      } else if (err.response?.data?.detail) {
        errMsg = err.response.data.detail;
      }
      setError(errMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAnalyze = () => {
    if (selectedFile) {
      executeAnalysis(selectedFile);
    }
  };

  return (
    <div className="app-container">
      <Header />

      <ErrorBanner
        error={error}
        warning={warning}
        onDismiss={() => setError(null)}
      />

      <UploadArea
        onFileSelect={handleFileSelect}
        onAnalyze={handleAnalyze}
        selectedFile={selectedFile}
        isProcessing={isProcessing}
        onClearFile={handleClearFile}
        onSelectSample={handleSelectSample}
      />

      {fileInfo && (
        <section className="results-dashboard">
          <SummaryCards fileInfo={fileInfo} />

          <MeasurementSummary summary={fileInfo.summary} />

          <MapPreview
            features={features}
            onSelectFeature={(feat) => setActiveModalFeature(feat)}
          />

          <FeatureTable
            features={features}
            onSelectFeature={(feat) => setActiveModalFeature(feat)}
          />
        </section>
      )}

      {activeModalFeature && (
        <FeatureModal
          feature={activeModalFeature}
          crs={fileInfo?.crs}
          onClose={() => setActiveModalFeature(null)}
        />
      )}

      <footer className="app-footer">
        <p>
          Geospatial File Measurement &copy; {new Date().getFullYear()} &bull; Built with FastAPI, GeoPandas &amp; React &bull;{' '}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
          >
            API Docs (Swagger)
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
