"use client";

import { useState, useEffect } from "react";

interface ReportSection {
  id: string;
  title: string;
}

interface ReportNavigationProps {
  sections: ReportSection[];
}

export default function ReportNavigation({ sections }: ReportNavigationProps) {
  const [activeSection, setActiveSection] = useState<string>(sections[0]?.id || "");

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + 200;
      for (const section of sections) {
        const el = document.getElementById(section.id);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            setActiveSection(section.id);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [sections]);

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      const top = el.getBoundingClientRect().top + window.scrollY - 100;
      window.scrollTo({ top, behavior: "smooth" });
      setActiveSection(id);
    }
  };

  return (
    <>
      {/* Mobile selector dropdown */}
      <div className="lg:hidden mb-6 border border-vo-border bg-vo-dark p-3">
        <label className="block text-[10px] font-mono font-bold text-vo-muted uppercase mb-1.5">
          JUMP TO SECTION
        </label>
        <select
          value={activeSection}
          onChange={(e) => scrollToSection(e.target.value)}
          className="w-full bg-vo-black border border-vo-border text-vo-white px-3 py-2 text-xs font-mono focus:border-vo-red focus:outline-none"
        >
          {sections.map((s, idx) => (
            <option key={s.id} value={s.id}>
              {idx + 1}. {s.title}
            </option>
          ))}
        </select>
      </div>

      {/* Desktop sticky sidebar navigation */}
      <div className="hidden lg:block sticky top-24 border border-vo-border bg-vo-dark p-4 max-h-[calc(100vh-140px)] overflow-y-auto">
        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-vo-border">
          <span className="w-2 h-2 bg-vo-red" />
          <h4 className="text-xs font-black uppercase tracking-wider text-vo-white">
            REPORT SECTIONS (20)
          </h4>
        </div>
        <nav className="space-y-1">
          {sections.map((s, idx) => {
            const isActive = activeSection === s.id;
            return (
              <button
                key={s.id}
                onClick={() => scrollToSection(s.id)}
                className={`w-full text-left px-2.5 py-1.5 text-xs font-mono transition-colors flex items-center gap-2 ${
                  isActive
                    ? "bg-vo-red text-white font-bold"
                    : "text-vo-muted hover:text-vo-white hover:bg-vo-black"
                }`}
              >
                <span className="text-[10px] opacity-70 w-5">
                  {String(idx + 1).padStart(2, "0")}
                </span>
                <span className="truncate">{s.title}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </>
  );
}
