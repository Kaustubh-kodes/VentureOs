// ---------------------------------------------------------------------------
// API response types
// ---------------------------------------------------------------------------

export interface HealthResponse {
  status: string;
  service: string;
}

export interface RootResponse {
  message: string;
}

// ---------------------------------------------------------------------------
// Startup form types
// ---------------------------------------------------------------------------

export type Industry =
  | "EdTech"
  | "FinTech"
  | "HealthTech"
  | "SaaS"
  | "AI"
  | "E-commerce"
  | "Other";

export type Budget =
  | "Under $10,000"
  | "$10,000-$50,000"
  | "$50,000+";

export type Timeline =
  | "1-3 months"
  | "3-6 months"
  | "6-12 months"
  | "12+ months";

export interface StartupFormData {
  startupIdea: string;
  targetAudience: string;
  industry: Industry | "";
  budget: Budget | "";
  timeline: Timeline | "";
  additionalContext: string;
}

export interface FormErrors {
  startupIdea?: string;
  targetAudience?: string;
  industry?: string;
}

// ---------------------------------------------------------------------------
// Agent types (used in hero preview — no API connection yet)
// ---------------------------------------------------------------------------

export type AgentStatus = "ANALYSING" | "WAITING" | "COMPLETE";

export interface Agent {
  id: string;
  name: string;
  status: AgentStatus;
}

// ---------------------------------------------------------------------------
// Phase 3 — CEO Agent Analysis types
// ---------------------------------------------------------------------------

export interface StartupAnalysisRequest {
  startup_idea: string;
  target_audience: string;
  industry: string;
  budget: string;
  timeline: string;
  notes?: string;
}

export interface CEOAnalysis {
  vision_statement: string;
  mission_statement: string;
  problem_definition: string;
  business_model: string;
  revenue_streams: string[];
  competitive_advantage: string;
  target_market_description: string;
  key_performance_indicators: string[];
  success_metrics: string[];
  go_to_market_summary: string;
  founding_team_requirements: string[];
  first_90_days_priorities: string[];
}

export interface KnowledgeSource {
  document: string;
  document_name?: string;
  page?: number | null;
}

export interface CEOAnalysisResponse {
  success: boolean;
  session_id?: string;
  status?: string;
  sources_used?: KnowledgeSource[];
  data: CEOAnalysis;
}

// ---------------------------------------------------------------------------
// Phase 4 — Supabase Startup Session & Agent Output types
// ---------------------------------------------------------------------------

export interface StartupSession {
  id: string;
  startup_idea: string;
  target_audience: string;
  industry: string;
  budget: string;
  timeline: string;
  notes?: string | null;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface AgentOutput {
  id?: string;
  session_id: string;
  agent_name: string;
  status: string;
  output?: Record<string, unknown> | null;
  output_json?: Record<string, unknown> | null;
  error_message?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface SessionDetailsResponse {
  success: boolean;
  session: StartupSession;
  agent_outputs: AgentOutput[];
}

export interface SessionListResponse {
  success: boolean;
  total: number;
  limit: number;
  offset: number;
  sessions: StartupSession[];
}

// ---------------------------------------------------------------------------
// Phase 5 — RAG Knowledge Base & Document Intelligence types
// ---------------------------------------------------------------------------

export interface KnowledgeDocument {
  id: string;
  session_id?: string | null;
  filename: string;
  file_type: string;
  file_size?: number | null;
  title?: string | null;
  description?: string | null;
  storage_path?: string | null;
  status: "processing" | "completed" | "failed";
  total_chunks: number;
  error_message?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DocumentUploadResponse {
  success: boolean;
  id: string;
  filename: string;
  file_type: string;
  file_size?: number | null;
  status: string;
  total_chunks: number;
  message: string;
}

export interface DocumentListResponse {
  success: boolean;
  total: number;
  documents: KnowledgeDocument[];
}

export interface DocumentStatusResponse {
  success: boolean;
  id: string;
  filename: string;
  status: string;
  total_chunks: number;
  error_message?: string | null;
}

// ---------------------------------------------------------------------------
// Phase 6 — Multi-Agent Intelligence & Final Report Synthesis types
// ---------------------------------------------------------------------------

export interface ConflictingAssessment {
  area: string;
  agent_a: string;
  agent_a_view: string;
  agent_b: string;
  agent_b_view: string;
  analysis: string;
}

export interface SynthesisReport {
  agent: string;
  executive_summary: string;
  startup_overview: string;
  problem: string;
  solution: string;
  target_customers: string[];
  market_opportunity: string;
  competitive_position: string;
  product_strategy: string;
  mvp_recommendation: string;
  gtm_strategy: string;
  business_model: string;
  financial_assessment: string;
  key_risks: string[];
  critical_assumptions: string[];
  investment_readiness: string;
  investment_score: number;
  top_5_priorities: string[];
  action_plan_30_days: string[];
  action_plan_90_days: string[];
  final_verdict: string;
  conflicting_assessments: ConflictingAssessment[];
  sources_used: KnowledgeSource[];
}

export interface AgentExecutionLog {
  id?: string;
  session_id: string;
  agent_name: string;
  event_type: string;
  message: string;
  metadata?: Record<string, unknown>;
  created_at?: string | null;
}

export interface AgentStatusInfo {
  name: string;
  display_name: string;
  agent_name?: string; // backwards compatibility
  status: "pending" | "processing" | "completed" | "failed";
  sources_count: number;
  started_at?: string | null;
  completed_at?: string | null;
  duration_ms?: number | null;
  error_message?: string | null;
}

export interface MultiAgentStatusResponse {
  success: boolean;
  session_id: string;
  overall_status?: string;
  session_status: string;
  progress_percentage?: number;
  overall_progress: number;
  current_agent?: string | null;
  started_at?: string | null;
  updated_at?: string | null;
  agents: AgentStatusInfo[] | Record<string, AgentStatusInfo>;
  agents_map?: Record<string, AgentStatusInfo>;
  has_final_report: boolean;
  events_count?: number;
  logs_count: number;
}

export interface MultiAgentRunResponse {
  success: boolean;
  session_id: string;
  message: string;
}

// ---------------------------------------------------------------------------
// Phase 7 — Observability Events, Evidence Labels & History types
// ---------------------------------------------------------------------------

export type EvidenceType = "EVIDENCE" | "AI ANALYSIS" | "ASSUMPTION";

export interface AnalysisEventItem {
  id?: string;
  timestamp: string;
  agent_name: string;
  event_type: string;
  message: string;
  metadata?: Record<string, unknown>;
}

export interface AnalysisEventsResponse {
  success: boolean;
  session_id: string;
  events: AnalysisEventItem[];
}

export interface AnalysisHistoryItem {
  id: string;
  startup_idea: string;
  industry: string;
  target_audience: string;
  budget: string;
  timeline: string;
  status: string;
  investment_score?: number | null;
  investment_readiness?: string | null;
  sources_count: number;
  created_at?: string | null;
}

export interface PaginatedAnalysisHistoryResponse {
  success: boolean;
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: AnalysisHistoryItem[];
}

// ---------------------------------------------------------------------------
// Phase 8 + 9 — Session Observability & System Metrics
// ---------------------------------------------------------------------------

export interface SessionMetrics {
  session_id: string;
  status: string;
  agents_total: number;
  agents_completed: number;
  agents_failed: number;
  total_duration_ms: number;
  total_duration_formatted: string;
  total_llm_calls: number;
  total_tokens: number | null;
  total_rag_chunks_retrieved: number;
  total_retries: number;
}

export interface SessionMetricsResponse {
  success: boolean;
  metrics: SessionMetrics;
}

