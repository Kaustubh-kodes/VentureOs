"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-vo-dark border-t border-vo-border py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <p className="text-vo-white font-black text-lg tracking-widest mb-2">VENTUREOS</p>
            <p className="text-vo-muted text-sm leading-relaxed">
              AI-Powered Startup Strategy Room
            </p>
          </div>

          {/* Navigation */}
          <div>
            <p className="text-vo-white text-xs font-bold tracking-widest uppercase mb-4">Navigation</p>
            <div className="flex flex-col gap-2">
              {["How It Works", "Agents", "Capabilities"].map((item) => (
                <button
                  key={item}
                  onClick={() => {
                    const id = item.toLowerCase().replace(/ /g, "-");
                    const el = document.getElementById(id);
                    if (el) el.scrollIntoView({ behavior: "smooth" });
                  }}
                  className="text-left text-vo-muted text-sm hover:text-vo-white transition-colors duration-200"
                >
                  {item}
                </button>
              ))}
              <Link
                href="/analyse"
                className="text-left text-vo-muted text-sm hover:text-vo-white transition-colors duration-200"
              >
                Analyse
              </Link>
            </div>
          </div>

          {/* Status */}
          <div>
            <p className="text-vo-white text-xs font-bold tracking-widest uppercase mb-4">Status</p>
            <p className="text-vo-muted text-sm">Phase 1 — Foundation</p>
            <p className="text-vo-muted text-xs mt-1">Phase 3 will add AI agents</p>
          </div>
        </div>

        <div className="border-t border-vo-border pt-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-vo-muted text-xs">
            &copy; {new Date().getFullYear()} VentureOS. All rights reserved.
          </p>
          <p className="text-vo-muted text-xs">
            Built with FastAPI &amp; Next.js
          </p>
        </div>
      </div>
    </footer>
  );
}
