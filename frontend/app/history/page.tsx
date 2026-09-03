"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import { getAnalysisHistory } from "@/lib/api";
import { AnalysisHistoryItem, PaginatedAnalysisHistoryResponse } from "@/types";

export default function HistoryPage() {
  const [data, setData] = useState<PaginatedAnalysisHistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);

  const fetchHistory = async (page: number, status: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAnalysisHistory({
        page,
        page_size: 15,
        status: status === "all" ? undefined : status,
      });
      setData(res);
    } catch (err: any) {
      setError(err?.message || "Failed to load analysis history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(currentPage, statusFilter);
  }, [currentPage, statusFilter]);

  const getStatusBadge = (st: string) => {
    switch (st) {
      case "completed":
        return "text-green-400 border-green-800 bg-[#051408]";
      case "processing":
        return "text-yellow-400 border-yellow-700 bg-[#181205]";
      case "failed":
        return "text-vo-red border-vo-red bg-[#180808]";
      case "partially_completed":
        return "text-amber-400 border-amber-800 bg-[#150f05]";
      default:
        return "text-vo-muted border-vo-border bg-vo-dark";
    }
  };

  const getScoreBadge = (score?: number | null) => {
    if (score === null || score === undefined) return null;
    if (score >= 70) return "text-green-400 border-green-800 bg-[#051408]";
    if (score >= 45) return "text-yellow-400 border-yellow-700 bg-[#181205]";
    return "text-vo-red border-vo-red bg-[#180808]";
  };

  const filteredItems = (data?.items || []).filter((item) => {
    if (!searchTerm.trim()) return true;
    const query = searchTerm.toLowerCase();
    return (
      item.startup_idea.toLowerCase().includes(query) ||
      item.industry.toLowerCase().includes(query) ||
      item.target_audience.toLowerCase().includes(query)
    );
  });

  return (
    <div className="min-h-screen bg-vo-black text-vo-white flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-vo-border mb-8">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2.5 h-2.5 bg-vo-red" />
              <p className="text-vo-red text-xs font-black tracking-widest uppercase">
                INTELLIGENCE REPOSITORY
              </p>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-vo-white">
              VENTURE ANALYSIS HISTORY
            </h1>
            <p className="text-vo-muted text-xs font-mono mt-1">
              Persistent repository of synthesized venture blueprints, investment scores, and multi-agent outputs
            </p>
          </div>

          <Link
            href="/analyse"
            className="bg-vo-red text-white text-xs font-black px-5 py-3 tracking-widest uppercase hover:bg-vo-red-hover transition-colors inline-flex items-center gap-2 self-start"
          >
            LAUNCH NEW VENTURE ANALYSIS +
          </Link>
        </div>

        {/* Filter & Search Bar */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-8">
          {/* Search Box */}
          <div className="md:col-span-7">
            <input
              type="text"
              placeholder="Search startup idea, industry, or target audience..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-vo-dark border border-vo-border px-4 py-2.5 text-xs font-mono text-vo-white placeholder-vo-muted focus:border-vo-red focus:outline-none"
            />
          </div>

          {/* Status Filter Tabs */}
          <div className="md:col-span-5 flex flex-wrap items-center gap-1.5 font-mono text-xs">
            {["all", "completed", "partially_completed", "processing", "failed"].map((st) => (
              <button
                key={st}
                onClick={() => {
                  setStatusFilter(st);
                  setCurrentPage(1);
                }}
                className={`px-3 py-2 text-[10px] font-bold uppercase transition-colors border ${
                  statusFilter === st
                    ? "bg-vo-red border-vo-red text-white"
                    : "bg-vo-dark border-vo-border text-vo-muted hover:text-vo-white"
                }`}
              >
                {st.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="mb-6 border border-vo-red bg-[#180808] p-4 text-xs font-mono text-vo-red">
            ⚠ {error}
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="space-y-4 py-8">
            <div className="h-20 bg-vo-dark border border-vo-border animate-pulse" />
            <div className="h-20 bg-vo-dark border border-vo-border animate-pulse" />
            <div className="h-20 bg-vo-dark border border-vo-border animate-pulse" />
          </div>
        )}

        {/* Sessions List */}
        {!loading && filteredItems.length === 0 ? (
          <div className="border border-vo-border bg-vo-dark p-12 text-center">
            <p className="text-vo-muted font-mono text-xs uppercase mb-3">
              NO ANALYSIS SESSIONS FOUND
            </p>
            <p className="text-vo-muted text-xs max-w-md mx-auto mb-6">
              You haven't run any analyses matching this filter yet. Submit a startup idea to generate your first venture blueprint.
            </p>
            <Link
              href="/analyse"
              className="bg-vo-red text-white text-xs font-black px-4 py-2 uppercase hover:bg-vo-red-hover transition-colors inline-block"
            >
              Start Venture Analysis →
            </Link>
          </div>
        ) : !loading && (
          <div className="space-y-4">
            {filteredItems.map((item) => (
              <Link
                key={item.id}
                href={`/analyse?session_id=${item.id}`}
                className="block border border-vo-border bg-vo-dark hover:border-vo-red transition-all p-5 sm:p-6 group"
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  {/* Left: Idea & Details */}
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`text-[9px] font-mono font-bold uppercase px-2 py-0.5 border ${getStatusBadge(item.status)}`}>
                        {item.status.replace(/_/g, " ")}
                      </span>
                      <span className="text-[10px] font-mono text-vo-red font-bold uppercase bg-[#180808] border border-vo-red/40 px-2 py-0.5">
                        {item.industry || "General"}
                      </span>
                      {item.sources_count > 0 && (
                        <span className="text-[10px] font-mono text-green-400 bg-[#051408] border border-green-900 px-2 py-0.5">
                          📄 {item.sources_count} sources
                        </span>
                      )}
                      <span className="text-[10px] font-mono text-vo-muted">
                        {item.created_at ? new Date(item.created_at).toLocaleDateString([], { year: "numeric", month: "short", day: "numeric" }) : ""}
                      </span>
                    </div>

                    <h3 className="text-base sm:text-lg font-black uppercase tracking-tight text-vo-white group-hover:text-vo-red transition-colors line-clamp-2">
                      {item.startup_idea}
                    </h3>

                    <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-vo-muted">
                      <span>AUDIENCE: <strong className="text-vo-white">{item.target_audience || "N/A"}</strong></span>
                      <span>BUDGET: <strong className="text-vo-white">{item.budget || "N/A"}</strong></span>
                      <span>TIMELINE: <strong className="text-vo-white">{item.timeline || "N/A"}</strong></span>
                    </div>
                  </div>

                  {/* Right: Investment Score & Action */}
                  <div className="flex items-center gap-6 lg:border-l lg:border-vo-border lg:pl-6">
                    {item.investment_score !== null && item.investment_score !== undefined ? (
                      <div className="text-right">
                        <span className="block text-[10px] font-mono text-vo-muted uppercase">
                          INVESTMENT SCORE
                        </span>
                        <span className={`inline-block font-mono font-black text-xl px-2 py-0.5 border mt-1 ${getScoreBadge(item.investment_score)}`}>
                          {item.investment_score} / 100
                        </span>
                      </div>
                    ) : (
                      <div className="text-right">
                        <span className="block text-[10px] font-mono text-vo-muted uppercase">
                          INVESTMENT SCORE
                        </span>
                        <span className="inline-block font-mono text-xs text-vo-muted mt-1 italic">
                          (Pending)
                        </span>
                      </div>
                    )}

                    <div className="text-vo-red font-mono text-sm font-black group-hover:translate-x-1 transition-transform">
                      OPEN →
                    </div>
                  </div>
                </div>
              </Link>
            ))}

            {/* Pagination Controls */}
            {data && data.total_pages > 1 && (
              <div className="flex items-center justify-between pt-6 border-t border-vo-border font-mono text-xs">
                <span className="text-vo-muted">
                  Page {data.page} of {data.total_pages} ({data.total} total sessions)
                </span>
                <div className="flex items-center gap-2">
                  <button
                    disabled={currentPage <= 1}
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    className="px-3 py-1.5 border border-vo-border bg-vo-dark text-vo-white disabled:opacity-40 hover:border-vo-red transition-colors"
                  >
                    ← PREVIOUS
                  </button>
                  <button
                    disabled={currentPage >= data.total_pages}
                    onClick={() => setCurrentPage((p) => Math.min(data.total_pages, p + 1))}
                    className="px-3 py-1.5 border border-vo-border bg-vo-dark text-vo-white disabled:opacity-40 hover:border-vo-red transition-colors"
                  >
                    NEXT →
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
