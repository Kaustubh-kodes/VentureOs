"use client";

import { useState } from "react";
import { SynthesisReport } from "@/types";
import EvidenceBadge from "./EvidenceBadge";
import ReportNavigation from "./ReportNavigation";
import SessionMetricsCard from "./SessionMetricsCard";

interface SynthesisReportViewProps {
  report: SynthesisReport;
  sessionId: string;
  onBackToProgress: () => void;
  onReset: () => void;
}

const REPORT_SECTIONS = [
  { id: "sec-exec-summary", title: "Executive Summary" },
  { id: "sec-overview", title: "Startup Overview" },
  { id: "sec-problem", title: "Problem Definition" },
  { id: "sec-solution", title: "Solution & Moat" },
  { id: "sec-target-customers", title: "Target Customers & ICP" },
  { id: "sec-market-opp", title: "Market Opportunity & TAM" },
  { id: "sec-competitive", title: "Competitive Positioning" },
  { id: "sec-product", title: "Product Architecture" },
  { id: "sec-mvp", title: "MVP Recommendation" },
  { id: "sec-gtm", title: "Go-to-Market Strategy" },
  { id: "sec-business-model", title: "Business Model & Monetization" },
  { id: "sec-financial", title: "Financial & Unit Economics" },
  { id: "sec-risks", title: "Key Risks & Headwinds" },
  { id: "sec-assumptions", title: "Critical Assumptions" },
  { id: "sec-priorities", title: "Top 5 Priorities" },
  { id: "sec-action-30", title: "30-Day Action Plan" },
  { id: "sec-action-90", title: "90-Day Action Plan" },
  { id: "sec-investment-case", title: "Investment Score & Verdict" },
  { id: "sec-sources", title: "Knowledge Sources Used" },
];

export default function SynthesisReportView({
  report,
  sessionId,
  onBackToProgress,
  onReset,
}: SynthesisReportViewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = `# VentureOS Investor-Grade Strategy Report\nSession: ${sessionId}\nInvestment Score: ${report.investment_score}/100 | Readiness: ${report.investment_readiness}\nFinal Verdict: ${report.final_verdict}\n\n## 1. Executive Summary\n${report.executive_summary}\n\n## 2. Startup Overview\n${report.startup_overview}\n\n## 3. Problem\n${report.problem}\n\n## 4. Solution\n${report.solution}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return "text-green-400 border-green-800 bg-[#051408]";
    if (score >= 45) return "text-yellow-400 border-yellow-700 bg-[#181205]";
    return "text-vo-red border-vo-red bg-[#180808]";
  };

  const sourcesUsed = report.sources_used || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Header Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-vo-border">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToProgress}
            className="text-xs font-mono font-bold uppercase text-vo-muted hover:text-vo-white border border-vo-border px-3 py-1.5 transition-colors"
          >
            ← ORCHESTRATION BOARD
          </button>
          <span className="text-xs font-mono text-vo-muted hidden sm:inline">
            SESSION: {sessionId.slice(0, 8)}...
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleCopy}
            className="text-xs font-mono font-bold uppercase bg-vo-dark text-vo-white border border-vo-border hover:border-vo-red px-3 py-1.5 transition-colors"
          >
            {copied ? "✓ COPIED REPORT" : "COPY REPORT"}
          </button>
          <button
            onClick={onReset}
            className="text-xs font-mono font-bold uppercase bg-vo-red text-white hover:bg-vo-red-hover px-4 py-1.5 transition-colors"
          >
            NEW ANALYSIS +
          </button>
        </div>
      </div>

      {/* PART 12: Executive Overview Banner */}
      <div className="border border-vo-border bg-vo-dark p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2.5 h-2.5 bg-vo-red" />
          <p className="text-vo-red text-xs font-black tracking-widest uppercase">
            VENTUREOS SYNTHESIZED BLUEPRINT
          </p>
        </div>
        <h1 className="text-2xl sm:text-4xl font-black text-vo-white uppercase tracking-tight mb-6">
          INVESTOR-GRADE VENTURE REPORT
        </h1>

        {/* 4-Stat High Contrast Dashboard Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-vo-black border border-vo-border mb-6">
          <div className="border-l-2 border-vo-red pl-3">
            <span className="block text-[10px] font-mono text-vo-muted uppercase">INVESTMENT SCORE</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className={`text-2xl font-black font-mono px-2 py-0.5 border ${getScoreColor(report.investment_score)}`}>
                {report.investment_score} / 100
              </span>
            </div>
          </div>

          <div className="border-l-2 border-vo-border pl-3">
            <span className="block text-[10px] font-mono text-vo-muted uppercase">READINESS VERDICT</span>
            <span className="block text-sm font-bold text-vo-white uppercase mt-1">
              {report.final_verdict}
            </span>
          </div>

          <div className="border-l-2 border-vo-border pl-3">
            <span className="block text-[10px] font-mono text-vo-muted uppercase">KNOWLEDGE COVERAGE</span>
            <span className="block text-sm font-bold text-green-400 mt-1">
              {sourcesUsed.length > 0 ? `${sourcesUsed.length} Founder Sources Used` : "Grounded on Startup Input"}
            </span>
          </div>

          <div className="border-l-2 border-vo-border pl-3">
            <span className="block text-[10px] font-mono text-vo-muted uppercase">ANALYSED BY</span>
            <span className="block text-sm font-bold text-vo-white mt-1">
              7 Specialised AI Agents
            </span>
          </div>
        </div>

        {/* Readiness Description Callout */}
        <div className="p-4 bg-vo-black/60 border border-vo-border/60">
          <span className="block text-[10px] font-mono font-bold text-vo-red uppercase tracking-wider mb-1">
            EXECUTIVE READINESS ASSESSMENT
          </span>
          <p className="text-xs font-mono leading-relaxed text-vo-white">
            {report.investment_readiness}
          </p>
        </div>
      </div>

      {/* Observability & Cost Metrics (Phase 8 + 9) */}
      <SessionMetricsCard sessionId={sessionId} />

      {/* PART 13: Conflicting Assessments Component */}
      {report.conflicting_assessments && report.conflicting_assessments.length > 0 && (
        <div className="border-2 border-vo-red bg-[#120505] p-6 sm:p-8">
          <div className="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-vo-red/40">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-vo-red animate-pulse" />
                <h3 className="text-sm font-black uppercase text-vo-red tracking-wider">
                  STRATEGIC CONTRADICTIONS DETECTED ({report.conflicting_assessments.length})
                </h3>
              </div>
              <p className="text-xs text-vo-muted mt-1">
                Contrarian disagreements surfaced between specialized agents that require founder validation.
              </p>
            </div>
            <EvidenceBadge type="ASSUMPTION" />
          </div>

          <div className="space-y-4">
            {report.conflicting_assessments.map((conflict, idx) => (
              <div key={idx} className="border border-vo-border bg-vo-black p-5 font-mono text-xs">
                <div className="flex items-center justify-between mb-3 pb-2 border-b border-vo-border">
                  <span className="text-vo-white font-black text-sm uppercase">
                    {idx + 1}. {conflict.area}
                  </span>
                  <span className="text-[10px] text-vo-red uppercase font-bold">
                    {conflict.agent_a} VS {conflict.agent_b}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="border border-vo-border/60 bg-vo-dark p-3">
                    <span className="block text-[10px] text-vo-muted font-bold uppercase mb-1">
                      {conflict.agent_a} FINDING:
                    </span>
                    <p className="text-vo-white text-xs leading-relaxed">{conflict.agent_a_view}</p>
                  </div>
                  <div className="border border-vo-red/40 bg-[#150707] p-3">
                    <span className="block text-[10px] text-vo-red font-bold uppercase mb-1">
                      {conflict.agent_b} COUNTERPOINT:
                    </span>
                    <p className="text-vo-white text-xs leading-relaxed">{conflict.agent_b_view}</p>
                  </div>
                </div>

                <div className="border-t border-vo-border/40 pt-3">
                  <strong className="text-green-400 text-[11px] uppercase">SYNTHESIS ANALYSIS &amp; VALIDATION: </strong>
                  <span className="text-vo-white">{conflict.analysis}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main 2-Column Content: Sticky Navigation + Report Sections */}
      <div className="grid grid-cols-12 gap-8">
        {/* Sticky Desktop Navigation Sidebar & Mobile Dropdown */}
        <div className="col-span-12 lg:col-span-3">
          <ReportNavigation sections={REPORT_SECTIONS} />
        </div>

        {/* Detailed Sections */}
        <div className="col-span-12 lg:col-span-9 space-y-6">
          {/* Section 1: Executive Summary */}
          <section id="sec-exec-summary" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                01. EXECUTIVE SUMMARY
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.executive_summary}
            </p>
          </section>

          {/* Section 2: Startup Overview */}
          <section id="sec-overview" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                02. STARTUP OVERVIEW
              </h3>
              <EvidenceBadge type={sourcesUsed.length > 0 ? "EVIDENCE" : "AI ANALYSIS"} />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.startup_overview}
            </p>
          </section>

          {/* Section 3: Problem Definition */}
          <section id="sec-problem" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                03. PROBLEM DEFINITION
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.problem}
            </p>
          </section>

          {/* Section 4: Solution & Moat */}
          <section id="sec-solution" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                04. SOLUTION &amp; STRATEGIC MOAT
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.solution}
            </p>
          </section>

          {/* Section 5: Target Customers */}
          <section id="sec-target-customers" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                05. TARGET CUSTOMERS &amp; ICP
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <ul className="space-y-2">
              {report.target_customers.map((c, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-mono text-vo-white">
                  <span className="text-vo-red">•</span>
                  <span>{c}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Section 6: Market Opportunity */}
          <section id="sec-market-opp" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                06. MARKET OPPORTUNITY &amp; TAM
              </h3>
              <EvidenceBadge type="ASSUMPTION" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.market_opportunity}
            </p>
          </section>

          {/* Section 7: Competitive Position */}
          <section id="sec-competitive" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                07. COMPETITIVE POSITIONING
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.competitive_position}
            </p>
          </section>

          {/* Section 8: Product Strategy */}
          <section id="sec-product" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                08. PRODUCT STRATEGY &amp; ARCHITECTURE
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.product_strategy}
            </p>
          </section>

          {/* Section 9: MVP Recommendation */}
          <section id="sec-mvp" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                09. MVP RECOMMENDATION &amp; SCOPE
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.mvp_recommendation}
            </p>
          </section>

          {/* Section 10: Go-to-Market */}
          <section id="sec-gtm" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                10. GO-TO-MARKET STRATEGY
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.gtm_strategy}
            </p>
          </section>

          {/* Section 11: Business Model */}
          <section id="sec-business-model" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                11. BUSINESS MODEL &amp; REVENUE DRIVERS
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.business_model}
            </p>
          </section>

          {/* Section 12: Financial Assessment */}
          <section id="sec-financial" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                12. FINANCIAL ASSESSMENT &amp; UNIT ECONOMICS
              </h3>
              <EvidenceBadge type="ASSUMPTION" />
            </div>
            <p className="text-xs font-mono leading-relaxed text-vo-muted whitespace-pre-line">
              {report.financial_assessment}
            </p>
          </section>

          {/* Section 13: Key Risks */}
          <section id="sec-risks" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                13. KEY RISKS &amp; HEADWINDS
              </h3>
              <EvidenceBadge type="ASSUMPTION" />
            </div>
            <ul className="space-y-2">
              {report.key_risks.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-mono text-vo-white">
                  <span className="text-vo-red font-bold">⚠</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Section 14: Critical Assumptions */}
          <section id="sec-assumptions" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                14. CRITICAL ASSUMPTIONS TO TEST
              </h3>
              <EvidenceBadge type="ASSUMPTION" />
            </div>
            <ul className="space-y-2">
              {report.critical_assumptions.map((a, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-mono text-vo-white">
                  <span className="text-yellow-400 font-bold">?</span>
                  <span>{a}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Section 15: Top 5 Priorities */}
          <section id="sec-priorities" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                15. TOP 5 PRIORITIES
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <ol className="space-y-2">
              {report.top_5_priorities.map((p, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-mono text-vo-white">
                  <span className="text-vo-red font-bold">{i + 1}.</span>
                  <span>{p}</span>
                </li>
              ))}
            </ol>
          </section>

          {/* Section 16: 30-Day Action Plan */}
          <section id="sec-action-30" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                16. 30-DAY EXECUTION PLAN
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <ul className="space-y-2">
              {report.action_plan_30_days.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-mono text-vo-white">
                  <span className="text-green-400">✓</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Section 17: 90-Day Action Plan */}
          <section id="sec-action-90" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                17. 90-DAY TRACTION PLAN
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <ul className="space-y-2">
              {report.action_plan_90_days.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-mono text-vo-white">
                  <span className="text-green-400">→</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Section 18: Investment Case & Verdict */}
          <section id="sec-investment-case" className="border border-vo-border bg-vo-dark p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-vo-border">
              <h3 className="text-sm font-black uppercase text-vo-white tracking-wider">
                18. INVESTMENT SCORE &amp; STRATEGIC VERDICT
              </h3>
              <EvidenceBadge type="AI ANALYSIS" />
            </div>
            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center gap-4">
                <span className="text-vo-muted">SCORE:</span>
                <span className={`px-2 py-0.5 font-bold border ${getScoreColor(report.investment_score)}`}>
                  {report.investment_score} / 100
                </span>
                <span className="text-vo-muted">VERDICT:</span>
                <span className="font-bold text-vo-white uppercase">{report.final_verdict}</span>
              </div>
              <p className="text-vo-muted leading-relaxed whitespace-pre-line pt-2">
                {report.investment_readiness}
              </p>
            </div>
          </section>

          {/* Section 19: Knowledge Sources Used */}
          <section id="sec-sources" className="border border-green-950 bg-[#051408]/40 p-6">
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-green-900/60">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-400" />
                <h3 className="text-sm font-black uppercase text-green-400 tracking-wider">
                  19. KNOWLEDGE BASE GROUNDING &amp; SOURCES USED
                </h3>
              </div>
              <EvidenceBadge type="EVIDENCE" />
            </div>

            {sourcesUsed.length > 0 ? (
              <div className="space-y-3 font-mono text-xs">
                <p className="text-vo-muted">
                  The following founder documents were retrieved and used by the multi-agent pipeline during this analysis:
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {sourcesUsed.map((s, idx) => (
                    <div key={idx} className="border border-green-900 bg-vo-black p-3 flex items-center gap-3">
                      <span className="text-lg">📄</span>
                      <div>
                        <span className="font-bold text-vo-white block">{s.document_name}</span>
                        <span className="text-[10px] text-vo-muted">
                          {s.page ? `Page ${s.page}` : "Uploaded Founder Knowledge Base"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-xs font-mono text-vo-muted italic">
                Analysis was generated from direct founder prompt input (no external document uploads attached).
              </p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
