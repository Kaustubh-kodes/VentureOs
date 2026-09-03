import {
  HealthResponse,
  RootResponse,
  StartupAnalysisRequest,
  CEOAnalysisResponse,
  SessionDetailsResponse,
  SessionListResponse,
  DocumentUploadResponse,
  DocumentListResponse,
  DocumentStatusResponse,
  KnowledgeDocument,
  MultiAgentStatusResponse,
  MultiAgentRunResponse,
  AgentExecutionLog,
  SynthesisReport,
  AnalysisEventsResponse,
  PaginatedAnalysisHistoryResponse,
  SessionMetricsResponse,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Generic fetch helper
// ---------------------------------------------------------------------------

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let errorDetail = res.statusText;
    try {
      const errorJson = await res.json();
      if (typeof errorJson.detail === "string") {
        errorDetail = errorJson.detail;
      } else if (Array.isArray(errorJson.detail) && errorJson.detail[0]?.msg) {
        errorDetail = errorJson.detail[0].msg;
      }
    } catch {
      // Use fallback status text if body is not json
    }
    throw new Error(errorDetail || `API error (${res.status})`);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Exported API functions
// ---------------------------------------------------------------------------

/** Check if the VentureOS backend is running and healthy. */
export async function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

/** Confirm root API availability. */
export async function getRoot(): Promise<RootResponse> {
  return apiFetch<RootResponse>("/");
}

/**
 * Execute CEO & Strategy analysis using Gemini through FastAPI with persistent session creation.
 */
export async function analyseCEO(
  data: StartupAnalysisRequest
): Promise<CEOAnalysisResponse> {
  return apiFetch<CEOAnalysisResponse>("/api/analyse/ceo", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Retrieve session details and associated agent outputs by session UUID.
 */
export async function getSession(sessionId: string): Promise<SessionDetailsResponse> {
  return apiFetch<SessionDetailsResponse>(`/api/sessions/${sessionId}`);
}

/**
 * Retrieve paginated list of recent startup sessions.
 */
export async function getSessions(limit = 20, offset = 0): Promise<SessionListResponse> {
  return apiFetch<SessionListResponse>(`/api/sessions?limit=${limit}&offset=${offset}`);
}

// ---------------------------------------------------------------------------
// Knowledge Base & Documents API
// ---------------------------------------------------------------------------

/**
 * Upload a document (PDF, DOCX, TXT, MD) to the knowledge base.
 */
export async function uploadDocument(
  file: File,
  sessionId?: string,
  title?: string
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (sessionId) formData.append("session_id", sessionId);
  if (title) formData.append("title", title);

  const url = `${API_URL}/api/documents/upload`;
  const res = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let errorDetail = res.statusText;
    try {
      const errorJson = await res.json();
      if (typeof errorJson.detail === "string") {
        errorDetail = errorJson.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail || `Upload failed (${res.status})`);
  }

  return res.json() as Promise<DocumentUploadResponse>;
}

/**
 * List all knowledge documents.
 */
export async function getDocuments(sessionId?: string): Promise<DocumentListResponse> {
  const query = sessionId ? `?session_id=${sessionId}` : "";
  return apiFetch<DocumentListResponse>(`/api/documents${query}`);
}

/**
 * Get single document metadata.
 */
export async function getDocument(documentId: string): Promise<KnowledgeDocument> {
  return apiFetch<KnowledgeDocument>(`/api/documents/${documentId}`);
}

/**
 * Check processing status of a document.
 */
export async function getDocumentStatus(documentId: string): Promise<DocumentStatusResponse> {
  return apiFetch<DocumentStatusResponse>(`/api/documents/${documentId}/status`);
}

/**
 * Delete a document and its associated vectors.
 */
export async function deleteDocument(
  documentId: string
): Promise<{ success: boolean; message: string }> {
  return apiFetch<{ success: boolean; message: string }>(`/api/documents/${documentId}`, {
    method: "DELETE",
  });
}

// ---------------------------------------------------------------------------
// Phase 6 — Multi-Agent Intelligence Pipeline API
// ---------------------------------------------------------------------------

/**
 * Creates a session and immediately triggers the full 7-agent intelligence pipeline.
 */
export async function startMultiAgentAnalysis(
  request: StartupAnalysisRequest
): Promise<MultiAgentRunResponse> {
  return apiFetch<MultiAgentRunResponse>("/api/analysis/start", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * Trigger the sequential 7-agent intelligence pipeline in the background.
 */
export async function runMultiAgentAnalysis(sessionId: string): Promise<MultiAgentRunResponse> {
  return apiFetch<MultiAgentRunResponse>(`/api/analysis/${sessionId}/run`, {
    method: "POST",
  });
}

/**
 * Poll live multi-agent progress, individual agent states, and progress %.
 */
export async function getAnalysisStatus(sessionId: string): Promise<MultiAgentStatusResponse> {
  return apiFetch<MultiAgentStatusResponse>(`/api/analysis/${sessionId}/status`);
}

/**
 * Fetch chronological execution logs for the live observability terminal.
 */
export async function getExecutionLogs(sessionId: string, limit = 100): Promise<AgentExecutionLog[]> {
  return apiFetch<AgentExecutionLog[]>(`/api/analysis/${sessionId}/logs?limit=${limit}`);
}

/**
 * Fetch all available agent outputs for a session.
 */
export async function getAllAgentsOutput(
  sessionId: string
): Promise<{ success: boolean; session_id: string; agents: Record<string, any> }> {
  return apiFetch<{ success: boolean; session_id: string; agents: Record<string, any> }>(
    `/api/analysis/${sessionId}/agents`
  );
}

/**
 * Fetch a single agent's structured output.
 */
export async function getSingleAgentOutput(
  sessionId: string,
  agentName: string
): Promise<{
  success: boolean;
  session_id: string;
  agent_name: string;
  status: string;
  output: any;
  error_message?: string;
}> {
  return apiFetch<{
    success: boolean;
    session_id: string;
    agent_name: string;
    status: string;
    output: any;
    error_message?: string;
  }>(`/api/analysis/${sessionId}/agents/${agentName}`);
}

/**
 * Retrieve the final synthesized 20-section Investor-Grade Report.
 */
export async function getFinalReport(
  sessionId: string
): Promise<{ success: boolean; session_id: string; status: string; report: SynthesisReport }> {
  return apiFetch<{ success: boolean; session_id: string; status: string; report: SynthesisReport }>(
    `/api/analysis/${sessionId}/report`
  );
}

/**
 * Retry an individual failed agent.
 */
export async function retryAgent(
  sessionId: string,
  agentName: string
): Promise<{ success: boolean; agent: string; output: any }> {
  return apiFetch<{ success: boolean; agent: string; output: any }>(
    `/api/analysis/${sessionId}/agents/${agentName}/retry`,
    {
      method: "POST",
    }
  );
}

/**
 * Fetch chronological observability events for real-time progress timeline.
 */
export async function getAnalysisEvents(
  sessionId: string,
  limit = 150
): Promise<AnalysisEventsResponse> {
  return apiFetch<AnalysisEventsResponse>(`/api/analysis/${sessionId}/events?limit=${limit}`);
}

/**
 * Fetch paginated venture analysis history with scores and readiness ratings.
 */
export async function getAnalysisHistory(params?: {
  page?: number;
  page_size?: number;
  status?: string;
}): Promise<PaginatedAnalysisHistoryResponse> {
  const query = new URLSearchParams();
  if (params?.page) query.append("page", String(params.page));
  if (params?.page_size) query.append("page_size", String(params.page_size));
  if (params?.status && params.status !== "all") query.append("status", params.status);

  const qs = query.toString() ? `?${query.toString()}` : "";
  return apiFetch<PaginatedAnalysisHistoryResponse>(`/api/analysis/history${qs}`);
}

/**
 * Fetch execution, duration, and RAG chunk metrics for a session (Phase 8 + 9).
 */
export async function getSessionMetrics(sessionId: string): Promise<SessionMetricsResponse> {
  return apiFetch<SessionMetricsResponse>(`/api/analysis/${sessionId}/metrics`);
}

/**
 * Fetch the latest system benchmark evaluation report.
 */
export async function getLatestEvaluation(): Promise<{ success: boolean; evaluation: any }> {
  return apiFetch<{ success: boolean; evaluation: any }>(`/api/evaluation/latest`);
}
