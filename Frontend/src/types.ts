// API Types for SEO Analyzer Frontend

export interface UserDetails {
  name: string;
  email: string;
  websiteUrl: string;
}

export interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  message?: string;
  duration?: number;
}

export interface AnalysisRequest {
  request_id: string;
  url: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  created_at: string;
}

export interface AgentResult {
  agent_name: string;
  success: boolean;
  result: string;
  duration_ms: number;
  error?: string;
}

export interface AnalysisResult {
  overallScore: number;
  report: string;
  issuesFound?: number;
  warnings?: number;
  passed?: number;
  categoryScores?: Record<string, number>;
  pdfAvailable?: boolean;
}

export interface AnalysisProgress {
  request_id: string;
  status: string;
  current_agent: string | null;
  agents: AgentStatus[];
}

export type AppStep = 'welcome' | 'form' | 'analyzing' | 'results';
