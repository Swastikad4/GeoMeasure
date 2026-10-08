import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 60000,
});

/**
 * Uploads a geospatial file (.kml or .zip) for processing
 * @param {File} file 
 * @param {Function} onProgress 
 */
export const uploadFile = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/files/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });

  return response.data;
};

/**
 * Retrieves file record details and summary
 * @param {string} fileId 
 */
export const getFile = async (fileId) => {
  const response = await apiClient.get(`/files/${fileId}/`);
  return response.data;
};

/**
 * Retrieves feature list with attributes, measurements, and GeoJSON
 * @param {string} fileId 
 */
export const getFeatures = async (fileId) => {
  const response = await apiClient.get(`/files/${fileId}/features/`);
  return response.data;
};

/**
 * Retrieves measurements array and aggregated metrics
 * @param {string} fileId 
 */
export const getMeasurements = async (fileId) => {
  const response = await apiClient.get(`/files/${fileId}/measurements/`);
  return response.data;
};

/**
 * Fetches sample test file as a File object
 * @param {string} sampleName 
 */
export const fetchSampleFile = async (sampleName) => {
  const response = await apiClient.get(`/files/samples/${sampleName}`, {
    responseType: 'blob',
  });
  return new File([response.data], sampleName, {
    type: sampleName.endsWith('.kml') ? 'application/vnd.google-earth.kml+xml' : 'application/zip',
  });
};

/**
 * Checks API server health
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Fetches recent files list
 */
export const getAllFiles = async () => {
  const response = await apiClient.get('/files/');
  return response.data;
};

export default {
  uploadFile,
  getFile,
  getFeatures,
  getMeasurements,
  checkHealth,
  getAllFiles,
};
