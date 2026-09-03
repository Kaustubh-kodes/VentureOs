"use client";

import { useEffect, useState } from "react";
import { SessionMetrics } from "@/types";
import { getSessionMetrics } from "@/lib/api";

interface SessionMetricsCardProps {
  sessionId: string;
}

export default function SessionMetricsCard({ sessionId }: SessionMetricsCardProps) {
  const [metrics, setMetrics] = useState<SessionMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function loadMetrics() {
      try {
        const res = await getSessionMetrics(sessionId);
        if (mounted && res.success && res.metrics) {
          setMetrics(res.metrics);
        }
      } catch (err) {
        // Non-intrusive fallback
      } finally {
        if (mounted) setLoading(false);
      }
    }
    loadMetrics();
    return () => {
      mounted = false;
    };
  }, [sessionId]);

  if (loading || !metrics) {
    return null;
  }

  return (
    <div className="border border-vo-border bg-vo-dark p-4 sm:p-5 font-mono text-xs">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-vo-border">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-vo-red" />
          <span className="text-[11px] font-black uppercase text-vo-white tracking-widest">
            EXECUTION &amp; OBSERVABILITY METRICS
          </span>
        </div>
        <span className="text-[10px] text-vo-muted uppercase">
          SESSION: {sessionId.slice(0, 8)}...
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="border border-vo-border bg-vo-black p-2.5">
          <span className="block text-[9px] text-vo-muted uppercase">AGENTS EXECUTED</span>
          <span className="block text-sm font-black text-vo-white mt-1">
            {metrics.agents_completed} / {metrics.agents_total}
          </span>
        </div>

        <div className="border border-vo-border bg-vo-black p-2.5">
          <span className="block text-[9px] text-vo-muted uppercase">TOTAL DURATION</span>
          <span className="block text-sm font-black text-green-400 mt-1">
            {metrics.total_duration_formatted}
          </span>
        </div>

        <div className="border border-vo-border bg-vo-black p-2.5">
          <span className="block text-[9px] text-vo-muted uppercase">RAG CHUNKS GROUNDED</span>
          <span className="block text-sm font-black text-vo-white mt-1">
            {metrics.total_rag_chunks_retrieved}
          </span>
        </div>

        <div className="border border-vo-border bg-vo-black p-2.5">
          <span className="block text-[9px] text-vo-muted uppercase">RETRIES</span>
          <span className="block text-sm font-black text-vo-white mt-1">
            {metrics.total_retries}
          </span>
        </div>

        <div className="border border-vo-border bg-vo-black p-2.5 col-span-2 sm:col-span-1">
          <span className="block text-[9px] text-vo-muted uppercase">TOKENS</span>
          <span className="block text-xs font-bold text-vo-muted mt-1">
            {metrics.total_tokens !== null ? metrics.total_tokens.toLocaleString() : "Provider Managed"}
          </span>
        </div>
      </div>
    </div>
  );
}
