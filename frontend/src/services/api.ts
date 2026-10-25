import {
  Capabilities,
  DemoCase,
  Investigation,
  InvestigationSummary,
  AssistantResponse,
  ResearchLabData,
  DetectionResult,
  ModelInfo
} from '../types';

const BASE_URL = '/api/v1';

export async function detectImage(file: File): Promise<DetectionResult> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('/api/detect', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: `Detection failed with status ${res.status}` }));
    throw new Error(errorData.detail || 'Failed to analyze image authenticity');
  }

  return res.json();
}

export async function fetchModelInfo(): Promise<ModelInfo> {
  const res = await fetch('/api/model-info');
  if (!res.ok) throw new Error('Failed to fetch model information');
  return res.json();
}

export async function fetchCapabilities(): Promise<Capabilities> {
  const res = await fetch(`${BASE_URL}/capabilities`);
  if (!res.ok) throw new Error('Failed to fetch system capabilities');
  return res.json();
}

export async function fetchDemoCases(): Promise<DemoCase[]> {
  const res = await fetch(`${BASE_URL}/demo-cases`);
  if (!res.ok) throw new Error('Failed to fetch demonstration cases');
  return res.json();
}


export async function createInvestigation(formData: FormData): Promise<Investigation> {
  const res = await fetch(`${BASE_URL}/investigations`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Investigation submission failed' }));
    throw new Error(err.detail || 'Submission failed');
  }
  return res.json();
}

export async function fetchInvestigations(params?: {
  skip?: number;
  limit?: number;
  status?: string;
  search?: string;
}): Promise<InvestigationSummary[]> {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set('skip', params.skip.toString());
  if (params?.limit !== undefined) query.set('limit', params.limit.toString());
  if (params?.status) query.set('status', params.status);
  if (params?.search) query.set('search', params.search);

  const res = await fetch(`${BASE_URL}/investigations?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch past investigations');
  return res.json();
}

export async function fetchInvestigation(id: string): Promise<Investigation> {
  const res = await fetch(`${BASE_URL}/investigations/${id}`);
  if (!res.ok) throw new Error('Failed to fetch investigation details');
  return res.json();
}

export async function deleteInvestigation(id: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/investigations/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete investigation');
}

export async function clearAllInvestigations(): Promise<void> {
  const res = await fetch(`${BASE_URL}/investigations?confirm=true`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to clear investigation history');
}

export async function reanalyzeInvestigation(id: string, mode: string): Promise<Investigation> {
  const res = await fetch(`${BASE_URL}/investigations/${id}/reanalyze?mode=${mode}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Re-analysis failed');
  return res.json();
}

export async function queryAssistant(investigationId: string, question: string): Promise<AssistantResponse> {
  const res = await fetch(`${BASE_URL}/assistant/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ investigation_id: investigationId, question }),
  });
  if (!res.ok) throw new Error('Assistant query failed');
  return res.json();
}

export async function fetchResearchLabData(): Promise<ResearchLabData> {
  const res = await fetch(`${BASE_URL}/research-lab`);
  if (!res.ok) throw new Error('Failed to load Research Lab data');
  return res.json();
}

export function getExportPdfUrl(id: string): string {
  return `${BASE_URL}/investigations/${id}/export/pdf`;
}

export function getExportJsonUrl(id: string): string {
  return `${BASE_URL}/investigations/${id}/export/json`;
}

export function getSanitizedImageUrl(id: string): string {
  return `${BASE_URL}/investigations/${id}/export/sanitized-image`;
}
