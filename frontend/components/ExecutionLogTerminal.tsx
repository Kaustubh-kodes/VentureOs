"use client";

import { useEffect, useRef } from "react";
import { AgentExecutionLog } from "@/types";

interface ExecutionLogTerminalProps {
  logs: AgentExecutionLog[];
  isLive?: boolean;
}

export default function ExecutionLogTerminal({ logs, isLive = true }: ExecutionLogTerminalProps) {
  const terminalBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const getEventBadgeColor = (eventType: string) => {
    if (eventType.includes("completed") || eventType.includes("passed")) return "text-green-400";
    if (eventType.includes("failed")) return "text-vo-red";
    if (eventType.includes("rag")) return "text-yellow-400";
    if (eventType.includes("started") || eventType.includes("llm")) return "text-sky-400";
    return "text-vo-muted";
  };

  return (
    <div className="border border-vo-border bg-vo-dark font-mono text-xs">
      {/* Terminal Top Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-vo-black border-b border-vo-border">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-vo-red" />
          <span className="text-vo-white text-[11px] font-black uppercase tracking-wider">
            LIVE AGENT OBSERVABILITY LOG
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isLive && (
            <span className="flex items-center gap-1.5 text-[10px] text-vo-red font-black uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-vo-red animate-pulse" />
              STREAMING
            </span>
          )}
          <span className="text-vo-muted text-[10px]">
            {logs.length} {logs.length === 1 ? "EVENT" : "EVENTS"}
          </span>
        </div>
      </div>

      {/* Terminal Output Area */}
      <div className="p-4 max-h-60 overflow-y-auto space-y-2 bg-[#080808]">
        {logs.length === 0 ? (
          <p className="text-vo-muted text-[11px] italic">Waiting for orchestrator events...</p>
        ) : (
          logs.map((log, idx) => (
            <div key={log.id || idx} className="flex items-start gap-2.5 leading-relaxed">
              <span className="text-vo-muted text-[10px] select-none">
                {idx + 1 < 10 ? `0${idx + 1}` : idx + 1}
              </span>
              <span className="text-vo-red font-bold uppercase text-[11px] min-w-[75px]">
                [{log.agent_name}]
              </span>
              <span className={`text-[10px] uppercase font-bold min-w-[130px] ${getEventBadgeColor(log.event_type)}`}>
                {log.event_type}
              </span>
              <span className="text-vo-white text-xs flex-1 break-words">
                {log.message}
              </span>
            </div>
          ))
        )}
        <div ref={terminalBottomRef} />
      </div>
    </div>
  );
}
