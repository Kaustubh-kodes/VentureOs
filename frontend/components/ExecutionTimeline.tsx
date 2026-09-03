"use client";

import { useEffect, useRef, useState } from "react";
import { AnalysisEventItem } from "@/types";

interface ExecutionTimelineProps {
  events: AnalysisEventItem[];
  isStreaming?: boolean;
}

export default function ExecutionTimeline({ events, isStreaming = false }: ExecutionTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [userHasScrolled, setUserHasScrolled] = useState(false);

  useEffect(() => {
    if (!userHasScrolled && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [events, userHasScrolled]);

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 40;
    setUserHasScrolled(!isAtBottom);
  };

  const formatTimestamp = (ts?: string) => {
    if (!ts) return "--:--:--";
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch {
      return ts.slice(11, 19);
    }
  };

  const getEventBadge = (eventType: string) => {
    if (eventType.includes("completed") || eventType.includes("passed")) {
      return "text-green-400 border-green-800 bg-[#051408]";
    }
    if (eventType.includes("failed") || eventType.includes("error")) {
      return "text-vo-red border-vo-red bg-[#180808]";
    }
    if (eventType.includes("retrieval") || eventType.includes("rag")) {
      return "text-yellow-400 border-yellow-700 bg-[#181205]";
    }
    return "text-sky-400 border-sky-800 bg-[#08121a]";
  };

  return (
    <div className="border border-vo-border bg-vo-dark font-mono text-xs">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-vo-black border-b border-vo-border">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-vo-red" />
          <span className="text-vo-white text-[11px] font-black uppercase tracking-wider">
            REAL-TIME EXECUTION TIMELINE
          </span>
        </div>
        <div className="flex items-center gap-3">
          {isStreaming && (
            <span className="flex items-center gap-1.5 text-[10px] text-vo-red font-black uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-vo-red animate-pulse" />
              STREAMING
            </span>
          )}
          <span className="text-vo-muted text-[10px]">
            {events.length} {events.length === 1 ? "EVENT" : "EVENTS"}
          </span>
        </div>
      </div>

      {/* Events Stream */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="p-4 max-h-64 overflow-y-auto space-y-2 bg-[#080808]"
      >
        {events.length === 0 ? (
          <p className="text-vo-muted text-[11px] italic">No execution events recorded yet.</p>
        ) : (
          events.map((ev, idx) => (
            <div key={ev.id || idx} className="flex flex-col sm:flex-row items-start sm:items-center gap-1.5 sm:gap-3 py-1 border-b border-vo-border/40 last:border-0 leading-relaxed">
              <span className="text-vo-muted text-[10px] select-none font-bold">
                [{formatTimestamp(ev.timestamp)}]
              </span>

              <span className="text-vo-red text-[10px] font-black uppercase tracking-wider min-w-[95px]">
                {ev.agent_name.toUpperCase()}
              </span>

              <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 border ${getEventBadge(ev.event_type)}`}>
                {ev.event_type.replace(/_/g, " ")}
              </span>

              <span className="text-vo-white text-xs flex-1 break-words">
                {ev.message}
              </span>
            </div>
          ))
        )}
      </div>

      {/* Bottom auto-scroll notification if user scrolled up */}
      {userHasScrolled && (
        <div className="px-4 py-1.5 bg-vo-black border-t border-vo-border flex items-center justify-between text-[10px] text-vo-muted">
          <span>Viewing past logs</span>
          <button
            onClick={() => {
              setUserHasScrolled(false);
              if (containerRef.current) containerRef.current.scrollTop = containerRef.current.scrollHeight;
            }}
            className="text-vo-red font-bold uppercase hover:underline"
          >
            Scroll to newest ↓
          </button>
        </div>
      )}
    </div>
  );
}
