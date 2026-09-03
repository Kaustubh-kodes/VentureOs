"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollTo = (id: string) => {
    setIsOpen(false);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-vo-black border-b border-vo-border" : "bg-transparent"
      }`}
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <Link
            href="/"
            className="text-vo-white font-black text-base tracking-widest hover:text-vo-red transition-colors duration-200"
            aria-label="VentureOS home"
          >
            VENTUREOS
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {[
              { label: "How It Works", id: "how-it-works" },
              { label: "Agents", id: "agents" },
              { label: "Capabilities", id: "capabilities" },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => scrollTo(item.id)}
                className="text-vo-muted text-xs tracking-widest hover:text-vo-white transition-colors duration-200 uppercase"
              >
                {item.label}
              </button>
            ))}
            <Link
              href="/knowledge"
              className="text-vo-muted text-xs tracking-widest hover:text-vo-red transition-colors duration-200 uppercase font-bold"
            >
              Knowledge Base
            </Link>
            <Link
              href="/history"
              className="text-vo-muted text-xs tracking-widest hover:text-vo-red transition-colors duration-200 uppercase font-bold"
            >
              History
            </Link>
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:block">
            <Link
              href="/analyse"
              className="bg-vo-red text-white text-xs font-black px-5 py-2.5 tracking-widest uppercase hover:bg-vo-red-hover transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-vo-red"
            >
              Analyse Your Startup
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden flex flex-col justify-center gap-1.5 p-2 w-10 h-10"
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? "Close menu" : "Open menu"}
            aria-expanded={isOpen}
          >
            <span
              className={`block w-5 h-0.5 bg-vo-white transition-all duration-300 origin-center ${
                isOpen ? "rotate-45 translate-y-2" : ""
              }`}
            />
            <span
              className={`block w-5 h-0.5 bg-vo-white transition-all duration-300 ${
                isOpen ? "opacity-0 scale-x-0" : ""
              }`}
            />
            <span
              className={`block w-5 h-0.5 bg-vo-white transition-all duration-300 origin-center ${
                isOpen ? "-rotate-45 -translate-y-2" : ""
              }`}
            />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div
        className={`md:hidden overflow-hidden transition-all duration-300 bg-vo-dark border-b border-vo-border ${
          isOpen ? "max-h-72 opacity-100" : "max-h-0 opacity-0"
        }`}
        aria-hidden={!isOpen}
      >
        <div className="px-4 py-4 flex flex-col gap-1">
          {[
            { label: "How It Works", id: "how-it-works" },
            { label: "Agents", id: "agents" },
            { label: "Capabilities", id: "capabilities" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => scrollTo(item.id)}
              className="text-left text-vo-muted text-xs tracking-widest hover:text-vo-white transition-colors duration-200 uppercase py-3 border-b border-vo-border last:border-0"
            >
              {item.label}
            </button>
          ))}
          <Link
            href="/knowledge"
            onClick={() => setIsOpen(false)}
            className="text-left text-vo-muted text-xs tracking-widest hover:text-vo-white transition-colors duration-200 uppercase py-3 border-b border-vo-border"
          >
            Knowledge Base
          </Link>
          <Link
            href="/history"
            onClick={() => setIsOpen(false)}
            className="text-left text-vo-muted text-xs tracking-widest hover:text-vo-white transition-colors duration-200 uppercase py-3 border-b border-vo-border"
          >
            History
          </Link>
          <Link
            href="/analyse"
            onClick={() => setIsOpen(false)}
            className="mt-3 bg-vo-red text-white text-xs font-black px-5 py-3 tracking-widest uppercase text-center hover:bg-vo-red-hover transition-colors duration-200"
          >
            Analyse Your Startup
          </Link>
        </div>
      </div>
    </nav>
  );
}
