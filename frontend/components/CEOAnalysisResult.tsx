"use client";

import { useState } from "react";
import { CEOAnalysis, KnowledgeSource } from "@/types";

interface CEOAnalysisResultProps {
  analysis: CEOAnalysis;
  sessionId?: string;
  sourcesUsed?: KnowledgeSource[];
  onLaunchMultiAgent?: () => void;
  onReset: () => void;
}

export default function CEOAnalysisResult({
  analysis,
  sessionId,
  sourcesUsed,
  onLaunchMultiAgent,
  onReset,
}: CEOAnalysisResultProps) {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(true);

  const handleCopy = () => {
    const markdown = `# VentureOS — CEO & Strategy Report

## Vision
${analysis.vision_statement}

## Mission
${analysis.mission_statement}

## The Problem
${analysis.problem_definition}

## Target Market
${analysis.target_market_description}

## Business Model
${analysis.business_model}

## Revenue Streams
${analysis.revenue_streams.map((s) => `- ${s}`).join("\n")}

## Competitive Advantage
${analysis.competitive_advantage}

## Go-To-Market Summary
${analysis.go_to_market_summary}

## Key KPIs
${analysis.key_performance_indicators.map((k) => `- ${k}`).join("\n")}

## Success Metrics
${analysis.success_metrics.map((m) => `- ${m}`).join("\n")}

## Founding Team Requirements
${analysis.founding_team_requirements.map((r) => `- ${r}`).join("\n")}

## First 90 Days Priorities
${analysis.first_90_days_priorities.map((p, i) => `${i + 1}. ${p}`).join("\n")}
`;
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Report Header Bar */}
      <div className="border border-vo-border bg-vo-dark p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-vo-red" />
            <span className="text-vo-red text-xs font-black tracking-widest uppercase">
              CEO &amp; STRATEGY REPORT
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black tracking-tight text-vo-white uppercase">
            VENTURE STRATEGY BLUEPRINT
          </h2>
          <div className="flex flex-wrap items-center gap-3 mt-1.5">
            <p className="text-vo-muted text-xs">Validated structured analysis by CEO Agent</p>
            {sessionId && (
              <span className="text-[10px] font-mono font-medium text-vo-muted border border-vo-border px-2 py-0.5 bg-vo-black">
                SESSION: {sessionId}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button
            onClick={handleCopy}
            className="flex-1 sm:flex-initial border border-vo-border text-vo-white text-xs font-bold px-4 py-2.5 uppercase tracking-wider hover:border-vo-red transition-colors duration-200"
          >
            {copied ? "COPIED TO CLIPBOARD" : "COPY REPORT"}
          </button>
          <button
            onClick={onReset}
            className="flex-1 sm:flex-initial border border-vo-border text-vo-white text-xs font-bold px-4 py-2.5 uppercase tracking-wider hover:border-vo-red transition-colors duration-200"
          >
            NEW ANALYSIS
          </button>
          {onLaunchMultiAgent && (
            <button
              onClick={onLaunchMultiAgent}
              className="flex-1 sm:flex-initial bg-vo-red text-white text-xs font-black px-4 py-2.5 uppercase tracking-widest hover:bg-vo-red-hover transition-colors duration-200"
            >
              RUN 7-AGENT INTELLIGENCE →
            </button>
          )}
        </div>
      </div>

      {/* Grounded Knowledge Sources Used Bar */}
      {sourcesUsed && sourcesUsed.length > 0 && (
        <div className="border border-vo-border bg-vo-dark p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-vo-red" />
              <p className="text-vo-white text-xs font-black tracking-widest uppercase">
                KNOWLEDGE SOURCES GROUNDING THIS ANALYSIS ({sourcesUsed.length})
              </p>
            </div>
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-vo-muted hover:text-vo-white text-[11px] font-mono uppercase"
            >
              {showSources ? "HIDE SOURCES" : "SHOW SOURCES"}
            </button>
          </div>
          {showSources && (
            <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-vo-border">
              {sourcesUsed.map((s, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-1.5 border border-vo-border bg-vo-black px-2.5 py-1 text-xs"
                >
                  <span className="text-vo-red font-bold">📄</span>
                  <span className="text-vo-white font-medium">{s.document}</span>
                  {s.page && (
                    <span className="text-vo-muted font-mono text-[10px]">
                      (Page {s.page})
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Grid: Vision & Mission */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="border-l-2 border-vo-red bg-vo-dark border-y border-r border-vo-border p-6">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-2">
            01 — VISION
          </span>
          <p className="text-vo-white text-base sm:text-lg font-medium leading-relaxed">
            &ldquo;{analysis.vision_statement}&rdquo;
          </p>
        </div>

        <div className="border-l-2 border-vo-border bg-vo-dark border-y border-r border-vo-border p-6 hover:border-l-vo-red transition-colors">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-2">
            02 — MISSION
          </span>
          <p className="text-vo-white text-base sm:text-lg font-medium leading-relaxed">
            &ldquo;{analysis.mission_statement}&rdquo;
          </p>
        </div>
      </div>

      {/* The Problem & Target Market */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="border border-vo-border bg-vo-dark p-6">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-3">
            03 — THE PROBLEM
          </span>
          <p className="text-vo-white text-sm sm:text-base leading-relaxed">
            {analysis.problem_definition}
          </p>
        </div>

        <div className="border border-vo-border bg-vo-dark p-6">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-3">
            04 — TARGET MARKET
          </span>
          <p className="text-vo-white text-sm sm:text-base leading-relaxed">
            {analysis.target_market_description}
          </p>
        </div>
      </div>

      {/* Business Model & Competitive Advantage */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="border border-vo-border bg-vo-dark p-6">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-3">
            05 — BUSINESS MODEL
          </span>
          <p className="text-vo-white text-sm sm:text-base leading-relaxed">
            {analysis.business_model}
          </p>
        </div>

        <div className="border border-vo-border bg-vo-dark p-6">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-3">
            06 — COMPETITIVE ADVANTAGE
          </span>
          <p className="text-vo-white text-sm sm:text-base leading-relaxed">
            {analysis.competitive_advantage}
          </p>
        </div>
      </div>

      {/* Revenue Streams */}
      <div className="border border-vo-border bg-vo-dark p-6">
        <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-4">
          07 — REVENUE STREAMS
        </span>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {analysis.revenue_streams.map((stream, idx) => (
            <div
              key={idx}
              className="border border-vo-border bg-vo-black p-4 flex items-start gap-3 hover:border-vo-red transition-colors"
            >
              <span className="text-vo-red font-black text-xs mt-0.5">0{idx + 1}</span>
              <p className="text-vo-white text-sm leading-snug">{stream}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Go To Market Summary */}
      <div className="border border-vo-border bg-vo-dark p-6">
        <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-3">
          08 — GO-TO-MARKET SUMMARY
        </span>
        <p className="text-vo-white text-sm sm:text-base leading-relaxed">
          {analysis.go_to_market_summary}
        </p>
      </div>

      {/* KPIs & Success Metrics */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="border border-vo-border bg-vo-dark p-6">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-4">
            09 — KEY KPIs
          </span>
          <ul className="space-y-2.5">
            {analysis.key_performance_indicators.map((kpi, idx) => (
              <li key={idx} className="flex items-start gap-3 text-sm text-vo-white">
                <span className="text-vo-red font-bold text-xs mt-0.5">•</span>
                <span>{kpi}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="border border-vo-border bg-vo-dark p-6">
          <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-4">
            10 — SUCCESS TRACTION METRICS
          </span>
          <ul className="space-y-2.5">
            {analysis.success_metrics.map((metric, idx) => (
              <li key={idx} className="flex items-start gap-3 text-sm text-vo-white">
                <span className="text-vo-red font-bold text-xs mt-0.5">•</span>
                <span>{metric}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Founding Team Requirements */}
      <div className="border border-vo-border bg-vo-dark p-6">
        <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-4">
          11 — FOUNDING TEAM REQUIREMENTS
        </span>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {analysis.founding_team_requirements.map((req, idx) => (
            <div
              key={idx}
              className="border border-vo-border bg-vo-black p-4 flex items-start gap-3 hover:border-vo-red transition-colors"
            >
              <span className="text-vo-red font-bold text-xs mt-0.5">REQ</span>
              <p className="text-vo-white text-sm leading-snug">{req}</p>
            </div>
          ))}
        </div>
      </div>

      {/* First 90 Days Priorities */}
      <div className="border border-vo-border bg-vo-dark p-6">
        <span className="text-vo-red text-[11px] font-black tracking-widest uppercase block mb-4">
          12 — FIRST 90 DAYS PRIORITIES
        </span>
        <div className="space-y-3">
          {analysis.first_90_days_priorities.map((priority, idx) => (
            <div
              key={idx}
              className="border border-vo-border bg-vo-black p-4 flex items-start gap-4 hover:border-vo-red transition-colors"
            >
              <span className="text-vo-red font-black text-sm tracking-wider">
                {String(idx + 1).padStart(2, "0")}
              </span>
              <p className="text-vo-white text-sm leading-relaxed">{priority}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
