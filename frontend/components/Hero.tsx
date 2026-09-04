"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

type AgentStatus = "ANALYSING" | "WAITING" | "COMPLETE";

interface Agent {
  id: string;
  name: string;
  status: AgentStatus;
}

const AGENTS: Agent[] = [
  { id: "ceo", name: "CEO", status: "WAITING" },
  { id: "market", name: "MARKET", status: "WAITING" },
  { id: "product", name: "PRODUCT", status: "WAITING" },
  { id: "marketing", name: "MARKETING", status: "WAITING" },
  { id: "finance", name: "FINANCE", status: "WAITING" },
  { id: "tech", name: "TECH", status: "WAITING" },
  { id: "skeptic", name: "SKEPTIC", status: "WAITING" },
  { id: "investment", name: "INVESTMENT", status: "WAITING" },
];

const STATUS_CONFIG: Record<AgentStatus, { dot: string; text: string; label: string }> = {
  ANALYSING: { dot: "bg-vo-red animate-pulse", text: "text-vo-red", label: "ANALYSING" },
  WAITING: { dot: "bg-vo-border", text: "text-vo-muted", label: "WAITING" },
  COMPLETE: { dot: "bg-green-600", text: "text-green-500", label: "COMPLETE" },
};

export default function Hero() {
  const [agents, setAgents] = useState<Agent[]>(AGENTS);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      setAgents((prev) =>
        prev.map((agent, i) => {
          if (i === index) return { ...agent, status: "ANALYSING" };
          if (i < index) return { ...agent, status: "COMPLETE" };
          return { ...agent, status: "WAITING" };
        })
      );
      index = (index + 1) % AGENTS.length;
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="min-h-screen flex items-center pt-16 bg-vo-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left: Text */}
          <div
            className={`transition-all duration-700 ${
              visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
            }`}
          >
            <p className="text-vo-red text-xs font-bold tracking-[0.3em] uppercase mb-6">
              AI-POWERED STRATEGY ROOM
            </p>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-black leading-none tracking-tight mb-8 text-vo-white">
              TURN YOUR
              <br />
              STARTUP IDEA
              <br />
              INTO{" "}
              <span className="text-vo-red">STRATEGY.</span>
            </h1>

            <p className="text-vo-muted text-lg sm:text-xl leading-relaxed mb-10 max-w-xl">
              VentureOS brings specialised AI agents into one strategy room to
              analyse your startup idea, challenge assumptions and build an
              actionable business strategy.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/analyse"
                className="bg-vo-red text-white font-black px-8 py-4 text-sm tracking-widest uppercase text-center hover:bg-vo-red-hover transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-vo-red"
              >
                Analyse Your Startup
              </Link>
              <button
                onClick={() => {
                  const el = document.getElementById("how-it-works");
                  if (el) el.scrollIntoView({ behavior: "smooth" });
                }}
                className="border border-vo-border text-vo-white font-black px-8 py-4 text-sm tracking-widest uppercase text-center hover:border-vo-border-hover transition-colors duration-200"
              >
                See How It Works
              </button>
            </div>
          </div>

          {/* Right: Agent Room Visual */}
          <div
            className={`transition-all duration-700 delay-150 ${
              visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
            }`}
          >
            <div className="border border-vo-border bg-vo-dark p-6">
              {/* Room header */}
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-vo-border">
                <div>
                  <p className="text-vo-white text-xs font-black tracking-widest uppercase">
                    STRATEGY ROOM
                  </p>
                  <p className="text-vo-muted text-xs mt-0.5">8 agents active</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-vo-red animate-pulse" />
                  <span className="text-vo-red text-xs font-black tracking-widest uppercase">LIVE</span>
                </div>
              </div>

              {/* Agents */}
              <div className="grid grid-cols-2 gap-3">
                {agents.map((agent) => {
                  const cfg = STATUS_CONFIG[agent.status];
                  return (
                    <div
                      key={agent.id}
                      className="border border-vo-border bg-vo-black p-3 hover:border-vo-red transition-all duration-200 cursor-default"
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-vo-white text-xs font-black tracking-widest">
                          {agent.name}
                        </span>
                        <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
                      </div>
                      <span className={`text-[10px] font-bold tracking-widest uppercase ${cfg.text}`}>
                        {cfg.label}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="mt-5 pt-4 border-t border-vo-border flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <p className="text-vo-muted text-xs">
                  <span className="text-vo-white font-semibold">7 Specialized Agents</span> active &amp; grounded in founder documents
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
