"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import StartupForm from "@/components/StartupForm";
import HealthStatus from "@/components/HealthStatus";
import MultiAgentProgressBoard from "@/components/MultiAgentProgressBoard";
import ExecutionTimeline from "@/components/ExecutionTimeline";
import SynthesisReportView from "@/components/SynthesisReportView";
import {
  getSessions,
  runMultiAgentAnalysis,
  getAnalysisStatus,
  getAllAgentsOutput,
  getAnalysisEvents,
  getExecutionLogs,
  getFinalReport,
  retryAgent,
} from "@/lib/api";
import {
  StartupSession,
  MultiAgentStatusResponse,
  AgentExecutionLog,
  AnalysisEventItem,
  SynthesisReport,
} from "@/types";

export default function AnalyseStrategyRoom() {
  const searchParams = useSearchParams();
  const urlSessionId = searchParams?.get("session_id");

  const [recentSessions, setRecentSessions] = useState<StartupSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(urlSessionId || null);
  const [viewMode, setViewMode] = useState<"form" | "progress" | "report">(urlSessionId ? "progress" : "form");

  // Multi-agent state
  const [statusData, setStatusData] = useState<MultiAgentStatusResponse | null>(null);
  const [allOutputs, setAllOutputs] = useState<Record<string, any>>({});
  const [events, setEvents] = useState<AnalysisEventItem[]>([]);
  const [logs, setLogs] = useState<AgentExecutionLog[]>([]);
  const [finalReport, setFinalReport] = useState<SynthesisReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  const fetchHistory = async () => {
    try {
      const res = await getSessions(6, 0);
      if (res.success && Array.isArray(res.sessions)) {
        setRecentSessions(res.sessions);
      }
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // If URL parameter changes, activate that session
  useEffect(() => {
    if (urlSessionId && urlSessionId !== activeSessionId) {
      setActiveSessionId(urlSessionId);
      setViewMode("progress");
    }
  }, [urlSessionId, activeSessionId]);

  // Reactive 2-Second Polling Loop for Active Session
  useEffect(() => {
    if (!activeSessionId || viewMode !== "progress") {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
      return;
    }

    const poll = async () => {
      try {
        const [statusRes, outputsRes, eventsRes] = await Promise.all([
          getAnalysisStatus(activeSessionId),
          getAllAgentsOutput(activeSessionId),
          getAnalysisEvents(activeSessionId, 150).catch(() => null),
        ]);

        if (statusRes.success) {
          setStatusData(statusRes);
        }
        if (outputsRes.success) {
          setAllOutputs(outputsRes.agents || {});
        }
        if (eventsRes?.success && Array.isArray(eventsRes.events)) {
          setEvents(eventsRes.events);
        }

        // Terminal state stop check
        const st = statusRes.session_status || statusRes.overall_status || "";
        if (["completed", "partially_completed", "failed"].includes(st)) {
          if (pollTimerRef.current) {
            clearInterval(pollTimerRef.current);
            pollTimerRef.current = null;
          }
          fetchHistory();
        }
      } catch {
        // network or server transient hiccups ignored during live poll
      }
    };

    poll();
    pollTimerRef.current = setInterval(poll, 2000);

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, [activeSessionId, viewMode]);

  const handleLaunchMultiAgent = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    setViewMode("progress");
    setErrorMessage(null);
    try {
      await runMultiAgentAnalysis(sessionId);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to start multi-agent analysis.");
    }
  };

  const handleSelectRecentSession = (session: StartupSession) => {
    setActiveSessionId(session.id);
    setViewMode("progress");
    setStatusData(null);
    setEvents([]);
  };

  const handleViewFinalReport = async () => {
    if (!activeSessionId) return;
    try {
      const res = await getFinalReport(activeSessionId);
      if (res.success && res.report) {
        setFinalReport(res.report);
        setViewMode("report");
      }
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Report is not ready yet.");
    }
  };

  const handleRetryAgent = async (agentName: string) => {
    if (!activeSessionId) return;
    try {
      await retryAgent(activeSessionId, agentName);
      const statusRes = await getAnalysisStatus(activeSessionId);
      setStatusData(statusRes);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : `Failed to retry agent ${agentName}`);
    }
  };

  const handleResetAll = () => {
    setActiveSessionId(null);
    setViewMode("form");
    setStatusData(null);
    setAllOutputs({});
    setEvents([]);
    setLogs([]);
    setFinalReport(null);
    setErrorMessage(null);
    fetchHistory();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
      {/* VIEW: Final 20-Section Investor Report */}
      {viewMode === "report" && finalReport && activeSessionId && (
        <SynthesisReportView
          report={finalReport}
          sessionId={activeSessionId}
          onBackToProgress={() => setViewMode("progress")}
          onReset={handleResetAll}
        />
      )}

      {/* VIEW: Live Multi-Agent Progress Board */}
      {viewMode === "progress" && activeSessionId && (
        <div className="space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-vo-border">
            <button
              onClick={handleResetAll}
              className="text-vo-red text-xs font-mono font-bold tracking-widest uppercase hover:underline flex items-center gap-2 self-start"
            >
              ← RETURN TO FORM
            </button>
            <div className="flex items-center gap-4 text-xs font-mono text-vo-muted">
              <span>
                SESSION: <strong className="text-vo-white">{activeSessionId.slice(0, 8)}...</strong>
              </span>
              <Link
                href="/history"
                className="text-vo-muted hover:text-vo-white hover:underline uppercase"
              >
                All Sessions →
              </Link>
            </div>
          </div>

          {errorMessage && (
            <div className="p-4 border border-vo-red bg-[#180808] text-vo-red text-xs font-mono">
              ⚠ {errorMessage}
            </div>
          )}

          {statusData ? (
            <div className="space-y-8">
              <MultiAgentProgressBoard
                statusData={statusData}
                allOutputs={allOutputs}
                logs={logs}
                onStartPipeline={() => activeSessionId && handleLaunchMultiAgent(activeSessionId)}
                onRetryAgent={handleRetryAgent}
                onViewReport={handleViewFinalReport}
              />

              {/* Real-time Execution Timeline */}
              <ExecutionTimeline
                events={events}
                isStreaming={statusData.session_status === "processing"}
              />
            </div>
          ) : (
            <div className="p-12 border border-vo-border bg-vo-dark text-center space-y-3">
              <span className="w-3 h-3 rounded-full bg-vo-red animate-ping inline-block" />
              <p className="text-vo-white text-sm font-bold uppercase tracking-wider font-mono">
                CONNECTING TO MULTI-AGENT ORCHESTRATOR...
              </p>
              <p className="text-vo-muted text-xs font-mono">
                Retrieving live agent states and execution telemetry from Supabase.
              </p>
            </div>
          )}
        </div>
      )}

      {/* VIEW: Startup Parameter Input Form */}
      {viewMode === "form" && (
        <div className="grid lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* Left Column — Context & Specs */}
          <div className="lg:col-span-5 space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="w-2 h-2 rounded-full bg-vo-red" />
                <p className="text-vo-red text-xs font-black tracking-widest uppercase">
                  STRATEGY ROOM · PHASE 7
                </p>
              </div>
              <h1 className="text-4xl sm:text-5xl font-black leading-none tracking-tight text-vo-white mb-6 uppercase">
                MULTI-AGENT
                <br />
                STRATEGY ROOM.
              </h1>
              <p className="text-vo-muted text-base leading-relaxed mb-6">
                Submit your startup parameters to trigger the 7-agent intelligence pipeline.
                Observe execution in real time with duration tracking, RAG grounding, and evidence classification.
              </p>
            </div>

            {/* Architecture Pipeline Specs */}
            <div className="border border-vo-border bg-vo-dark p-6 space-y-4">
              <h3 className="text-xs font-mono font-bold uppercase text-vo-white tracking-widest">
                INTELLIGENCE PIPELINE ARCHITECTURE
              </h3>
              <div className="space-y-3 text-xs font-mono text-vo-muted">
                <div className="flex items-start gap-2">
                  <span className="text-vo-red font-black">01</span>
                  <span><strong>CEO Agent:</strong> Core thesis, vision &amp; executive moat</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-vo-red font-black">02</span>
                  <span><strong>Market Agent:</strong> TAM, SAM, SOM &amp; competitive positioning</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-vo-red font-black">03</span>
                  <span><strong>Product Agent:</strong> Architecture, MVP features &amp; UX priorities</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-vo-red font-black">04</span>
                  <span><strong>Marketing Agent:</strong> Acquisition channels, ICP &amp; GTM motion</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-vo-red font-black">05</span>
                  <span><strong>Finance Agent:</strong> Unit economics, burn rate &amp; 18-mo runway</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-vo-red font-black">06</span>
                  <span><strong>Investment Agent:</strong> Contrarian stress-test &amp; readiness score</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-vo-red font-black">07</span>
                  <span><strong>Synthesis Agent:</strong> 20-section comprehensive investor blueprint</span>
                </div>
              </div>
            </div>

            {/* Recent Sessions List */}
            {recentSessions.length > 0 && (
              <div className="border border-vo-border bg-vo-dark p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-vo-border pb-3">
                  <h3 className="text-xs font-mono font-bold uppercase text-vo-white tracking-widest">
                    RECENT ANALYSES
                  </h3>
                  <Link
                    href="/history"
                    className="text-[10px] font-mono text-vo-red font-bold hover:underline uppercase"
                  >
                    View All History →
                  </Link>
                </div>
                <div className="space-y-2">
                  {recentSessions.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => handleSelectRecentSession(s)}
                      className="w-full text-left p-3 border border-vo-border bg-vo-black hover:border-vo-red transition-colors group"
                    >
                      <div className="flex items-center justify-between text-[10px] font-mono text-vo-muted mb-1">
                        <span className="text-vo-red uppercase font-bold">{s.industry || "Venture"}</span>
                        <span>{s.status}</span>
                      </div>
                      <p className="text-xs text-vo-white line-clamp-1 group-hover:text-vo-red transition-colors">
                        {s.startup_idea}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <HealthStatus />
          </div>

          {/* Right Column — Submission Form */}
          <div className="lg:col-span-7">
            <StartupForm
              onSuccess={() => {}}
              onLaunchMultiAgent={(sessionId) => {
                setActiveSessionId(sessionId);
                setViewMode("progress");
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
