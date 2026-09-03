"use client";

import { EvidenceType } from "@/types";

interface EvidenceBadgeProps {
  type: EvidenceType;
  sourceText?: string;
}

export default function EvidenceBadge({ type, sourceText }: EvidenceBadgeProps) {
  switch (type) {
    case "EVIDENCE":
      return (
        <span
          title={sourceText ? `Grounded in: ${sourceText}` : "Directly supported by founder knowledge"}
          className="inline-flex items-center gap-1.5 bg-[#051408] border border-green-800 text-green-400 font-mono font-bold px-2 py-0.5 text-[9px] uppercase tracking-wider select-none"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
          FOUNDER EVIDENCE
        </span>
      );
    case "ASSUMPTION":
      return (
        <span
          title="Unverified hypothesis requiring validation"
          className="inline-flex items-center gap-1.5 bg-[#181205] border border-yellow-700 text-yellow-400 font-mono font-bold px-2 py-0.5 text-[9px] uppercase tracking-wider select-none"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-yellow-400" />
          ASSUMPTION
        </span>
      );
    case "AI ANALYSIS":
    default:
      return (
        <span
          title="Generated AI strategic reasoning"
          className="inline-flex items-center gap-1.5 bg-[#180808] border border-vo-red text-vo-red font-mono font-bold px-2 py-0.5 text-[9px] uppercase tracking-wider select-none"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-vo-red" />
          AI ANALYSIS
        </span>
      );
  }
}
