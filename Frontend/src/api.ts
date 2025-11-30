import axios from 'axios';
import { AnalysisResult, AnalysisProgress } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Start a new SEO analysis
 */
export async function startAnalysis(
  url: string,
  name: string,
  email: string
): Promise<{ request_id: string }> {
  const response = await api.post('/api/analyze', {
    url,
    name,
    email,
  });
  return response.data;
}

/**
 * Get analysis progress/status
 */
export async function getAnalysisProgress(
  requestId: string
): Promise<AnalysisProgress> {
  const response = await api.get(`/api/analysis/${requestId}/progress`);
  return response.data;
}

/**
 * Get final analysis results
 */
export async function getAnalysisResults(
  requestId: string
): Promise<AnalysisResult> {
  const response = await api.get(`/api/analysis/${requestId}`);
  return response.data;
}

/**
 * Download PDF report
 */
export async function downloadPdfReport(requestId: string): Promise<Blob> {
  const response = await api.get(`/api/analysis/${requestId}/pdf`, {
    responseType: 'blob',
  });
  return response.data;
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await api.get('/api/health');
  return response.data;
}
