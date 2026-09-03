"use client";

import { useEffect } from "react";
import EvidenceBadge from "./EvidenceBadge";

interface AgentDetailModalProps {
  agentName: string;
  agentRole: string;
  status?: string;
  durationMs?: number | null;
  startedAt?: string | null;
  completedAt?: string | null;
  outputData: any;
  onClose: () => void;
}

export default function AgentDetailModal({
  agentName,
  agentRole,
  status = "completed",
  durationMs,
  startedAt,
  completedAt,
  outputData,
  onClose,
}: AgentDetailModalProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!outputData) return null;

  const sources = outputData.sources_used || [];

  const formatDuration = (ms?: number | null) => {
    if (!ms) return null;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-vo-dark border border-vo-border w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-vo-border bg-vo-black">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2 h-2 bg-vo-red" />
              <span className="text-[10px] font-mono font-bold uppercase text-vo-red tracking-wider">
                {agentName.toUpperCase()} AGENT
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 border border-green-800 text-green-400 bg-[#051408] uppercase font-bold">
                {status}
              </span>
              {durationMs && (
                <span className="text-[10px] font-mono px-2 py-0.5 border border-vo-border text-vo-white bg-vo-dark">
                  ⚡ {formatDuration(durationMs)}
                </span>
              )}
            </div>
            <h3 className="text-lg font-black uppercase text-vo-white tracking-wide">
              {agentRole}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-vo-muted hover:text-vo-white font-mono text-xs px-3 py-1.5 border border-vo-border hover:border-vo-red transition-colors"
          >
            [ESC] CLOSE ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Metadata banner */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-vo-black border border-vo-border font-mono text-xs">
            <div>
              <span className="block text-[10px] text-vo-muted uppercase">Duration</span>
              <span className="text-vo-white font-bold">{formatDuration(durationMs) || "N/A"}</span>
            </div>
            <div>
              <span className="block text-[10px] text-vo-muted uppercase">Sources Used</span>
              <span className="text-vo-white font-bold">{sources.length}</span>
            </div>
            <div>
              <span className="block text-[10px] text-vo-muted uppercase">Status</span>
              <span className="text-green-400 font-bold uppercase">{status}</span>
            </div>
            <div>
              <span className="block text-[10px] text-vo-muted uppercase">Output Format</span>
              <span className="text-vo-white font-bold">Pydantic JSON</span>
            </div>
          </div>

          {/* Sources section */}
          {sources.length > 0 && (
            <div className="border border-green-900/60 bg-[#051408]/40 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-bold text-green-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                  KNOWLEDGE SOURCES USED ({sources.length})
                </span>
                <EvidenceBadge type="EVIDENCE" />
              </div>
              <ul className="space-y-1 text-xs font-mono text-vo-white">
                {sources.map((s: any, idx: number) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="text-green-400">📄</span>
                    <span className="font-bold">{s.document_name}</span>
                    {s.page && <span className="text-vo-muted">(Page {s.page})</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Structured Deliverables */}
          <div className="space-y-4">
            {Object.entries(outputData).map(([key, value]) => {
              if (key === "sources_used" || key.startsWith("_")) return null;

              const isAssumption = key.includes("risk") || key.includes("assumption") || key.includes("validation");
              const labelType = isAssumption ? "ASSUMPTION" : "AI ANALYSIS";

              return (
                <div key={key} className="border border-vo-border bg-vo-black p-4">
                  <div className="flex items-center justify-between mb-2 pb-2 border-b border-vo-border">
                    <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-vo-white">
                      {key.replace(/_/g, " ")}
                    </h4>
                    <EvidenceBadge type={labelType} />
                  </div>

                  <div className="text-xs font-mono leading-relaxed text-vo-muted">
                    {typeof value === "string" ? (
                      <p className="whitespace-pre-line text-vo-white">{value}</p>
                    ) : Array.isArray(value) ? (
                      <ul className="space-y-1.5">
                        {value.map((item, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-vo-red mt-0.5">•</span>
                            <span className="text-vo-white">
                              {typeof item === "object" ? JSON.stringify(item) : String(item)}
                            </span>
                          </li>
                        ))}
                      </ul>
                    ) : typeof value === "object" && value !== null ? (
                      <div className="space-y-2">
                        {Object.entries(value).map(([subKey, subVal]) => (
                          <div key={subKey} className="border-l-2 border-vo-border pl-3 py-1">
                            <span className="text-vo-muted text-[11px] uppercase block font-bold">
                              {subKey.replace(/_/g, " ")}:
                            </span>
                            <span className="text-vo-white">
                              {typeof subVal === "object" ? JSON.stringify(subVal) : String(subVal)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-vo-white font-bold">{String(value)}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-vo-border bg-vo-black flex items-center justify-between text-xs font-mono text-vo-muted">
          <span>VENTUREOS VERIFIED OUTPUT</span>
          <button
            onClick={onClose}
            className="bg-vo-red text-white font-bold px-4 py-1.5 uppercase hover:bg-vo-red-hover transition-colors"
          >
            DONE
          </button>
        </div>
      </div>
    </div>
  );
}
