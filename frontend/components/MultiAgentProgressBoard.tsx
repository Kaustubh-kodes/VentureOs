"use client";

import { useState } from "react";
import { MultiAgentStatusResponse, AgentExecutionLog } from "@/types";
import AgentDetailModal from "./AgentDetailModal";

interface MultiAgentProgressBoardProps {
  statusData: MultiAgentStatusResponse;
  allOutputs: Record<string, any>;
  logs: AgentExecutionLog[];
  onStartPipeline?: () => void;
  onRetryAgent: (agentName: string) => Promise<void>;
  onViewReport: () => void;
}

const AGENT_ORDER = [
  { id: "ceo", role: "CEO & Strategy", desc: "Executive vision, core moat & thesis" },
  { id: "market", role: "Market Research", desc: "TAM/SAM/SOM, ICP & competitive landscape" },
  { id: "product", role: "Product Strategy", desc: "MVP features, core architecture & differentiation" },
  { id: "marketing", role: "Marketing & GTM", desc: "Acquisition channels, ICP persona & messaging" },
  { id: "finance", role: "Finance & Economics", desc: "Unit economics, burn rate & runway model" },
  { id: "investment", role: "Investment & Risk", desc: "Contrarian stress-testing & investment readiness score" },
  { id: "synthesis", role: "Final Synthesis", desc: "20-section comprehensive investor-grade blueprint" },
];

export default function MultiAgentProgressBoard({
  statusData,
  allOutputs,
  logs,
  onStartPipeline,
  onRetryAgent,
  onViewReport,
}: MultiAgentProgressBoardProps) {
  const [selectedAgent, setSelectedAgent] = useState<{ id: string; role: string } | null>(null);

  const getAgentInfo = (agentId: string) => {
    if (Array.isArray(statusData.agents)) {
      return statusData.agents.find((a) => a.name === agentId || a.agent_name === agentId);
    }
    return statusData.agents?.[agentId];
  };

  const getStatusBadge = (status?: string, durationMs?: number | null) => {
    switch (status) {
      case "completed":
        return (
          <div className="flex items-center gap-2">
            {durationMs ? (
              <span className="text-[10px] font-mono text-vo-muted bg-vo-dark px-1.5 py-0.5 border border-vo-border">
                {(durationMs / 1000).toFixed(1)}s
              </span>
            ) : null}
            <span className="text-[10px] font-mono font-bold uppercase text-green-400 border border-green-800 px-2 py-0.5 bg-[#051408] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
              COMPLETED ✓
            </span>
          </div>
        );
      case "processing":
        return (
          <span className="text-[10px] font-mono font-bold uppercase text-yellow-400 border border-yellow-700 px-2 py-0.5 bg-[#181205] flex items-center gap-1.5 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-ping" />
            ANALYSING ●
          </span>
        );
      case "failed":
        return (
          <span className="text-[10px] font-mono font-bold uppercase text-vo-red border border-vo-red px-2 py-0.5 bg-[#180808] flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-vo-red" />
            FAILED ✕
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-mono text-vo-muted border border-vo-border px-2 py-0.5 bg-vo-black flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-neutral-600" />
            WAITING ○
          </span>
        );
    }
  };

  const currentPercent = statusData.progress_percentage ?? statusData.overall_progress ?? 0;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner with Progress */}
      <div className="border border-vo-border bg-vo-dark p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2 h-2 rounded-full bg-vo-red animate-pulse" />
              <p className="text-vo-red text-xs font-black tracking-widest uppercase">
                INTELLIGENCE ORCHESTRATOR
              </p>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-vo-white uppercase tracking-tight">
              MULTI-AGENT VENTURE ANALYSIS
            </h2>
            <p className="text-vo-muted text-xs mt-1">
              Controlled sequential orchestration with shared pgvector RAG context chaining
            </p>
          </div>

          <div className="flex items-center gap-3">
            {onStartPipeline && !statusData.has_final_report && statusData.session_status !== "processing" && (
              <button
                onClick={onStartPipeline}
                className="bg-vo-red text-white text-xs font-black px-5 py-3 tracking-widest uppercase hover:bg-vo-red-hover transition-colors duration-200 animate-pulse shadow-lg"
              >
                RUN 7-AGENT INTELLIGENCE PIPELINE →
              </button>
            )}
            {statusData.has_final_report && (
              <button
                onClick={onViewReport}
                className="bg-vo-red text-white text-xs font-black px-5 py-3 tracking-widest uppercase hover:bg-vo-red-hover transition-colors duration-200"
              >
                VIEW FINAL REPORT →
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-vo-muted uppercase">
              STATUS: <strong className="text-vo-white">{statusData.session_status}</strong>
              {statusData.current_agent && (
                <span className="ml-2 text-vo-red font-bold">
                  (ACTIVE: {statusData.current_agent.toUpperCase()})
                </span>
              )}
            </span>
            <span className="text-vo-red font-bold text-sm">
              {currentPercent}% COMPLETED
            </span>
          </div>
          <div className="w-full bg-vo-black border border-vo-border h-3 p-0.5">
            <div
              className="bg-vo-red h-full transition-all duration-500 ease-out"
              style={{ width: `${currentPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {AGENT_ORDER.map((agent, index) => {
          const info = getAgentInfo(agent.id);
          const st = info?.status || "pending";
          const isCompleted = st === "completed";
          const isProcessing = st === "processing";
          const isFailed = st === "failed";
          const output = allOutputs[agent.id]?.output;

          return (
            <div
              key={agent.id}
              className={`border p-5 transition-all duration-200 flex flex-col justify-between ${
                isProcessing
                  ? "border-vo-red bg-[#120505] shadow-lg shadow-red-950/20"
                  : isCompleted
                  ? "border-vo-border bg-vo-dark hover:border-vo-red/60"
                  : isFailed
                  ? "border-vo-red/50 bg-[#120505]"
                  : "border-vo-border/40 bg-vo-black/60 opacity-70"
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-[10px] font-mono text-vo-muted">
                    0{index + 1} / 07
                  </span>
                  {getStatusBadge(st, info?.duration_ms)}
                </div>

                <h3 className="text-sm font-black uppercase tracking-wider text-vo-white mb-1">
                  {agent.role}
                </h3>
                <p className="text-xs text-vo-muted mb-4 leading-relaxed">
                  {agent.desc}
                </p>

                {info?.sources_count !== undefined && info.sources_count > 0 && (
                  <div className="mb-4 inline-flex items-center gap-1.5 text-[10px] font-mono text-green-400 bg-[#051408] border border-green-900 px-2 py-0.5">
                    <span>📄</span>
                    <span>{info.sources_count} Knowledge Sources Used</span>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-vo-border/40 flex items-center justify-between">
                {isCompleted && output ? (
                  <button
                    onClick={() => setSelectedAgent({ id: agent.id, role: agent.role })}
                    className="text-xs font-mono font-bold uppercase text-vo-red hover:underline flex items-center gap-1"
                  >
                    INSPECT FINDINGS →
                  </button>
                ) : isFailed ? (
                  <button
                    onClick={() => onRetryAgent(agent.id)}
                    className="text-xs font-mono font-bold uppercase text-vo-red border border-vo-red px-2.5 py-1 hover:bg-vo-red hover:text-white transition-colors"
                  >
                    RETRY AGENT
                  </button>
                ) : isProcessing ? (
                  <span className="text-[11px] font-mono text-yellow-400 animate-pulse">
                    Executing reasoning chain...
                  </span>
                ) : (
                  <span className="text-[11px] font-mono text-vo-muted">
                    Waiting for pipeline...
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <AgentDetailModal
          agentName={selectedAgent.id}
          agentRole={selectedAgent.role}
          status={getAgentInfo(selectedAgent.id)?.status || "completed"}
          durationMs={getAgentInfo(selectedAgent.id)?.duration_ms}
          startedAt={getAgentInfo(selectedAgent.id)?.started_at}
          completedAt={getAgentInfo(selectedAgent.id)?.completed_at}
          outputData={allOutputs[selectedAgent.id]?.output}
          onClose={() => setSelectedAgent(null)}
        />
      )}
    </div>
  );
}
