"use client";

import { useState, useEffect } from "react";
import { getHealth } from "@/lib/api";

type Status = "checking" | "connected" | "offline";

export default function HealthStatus() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    const check = async () => {
      try {
        await getHealth();
        setStatus("connected");
      } catch {
        setStatus("offline");
      }
    };
    check();
  }, []);

  const config = {
    checking: { dot: "bg-vo-muted animate-pulse", text: "text-vo-muted", label: "Checking API..." },
    connected: { dot: "bg-vo-red", text: "text-vo-muted", label: "API Connected" },
    offline: { dot: "bg-red-800", text: "text-red-500", label: "API Offline" },
  }[status];

  return (
    <div className="flex items-center gap-2" role="status" aria-live="polite">
      <span className={`w-2 h-2 rounded-full ${config.dot}`} aria-hidden="true" />
      <span className={`text-xs font-medium tracking-wider ${config.text}`}>
        {config.label}
      </span>
    </div>
  );
}
