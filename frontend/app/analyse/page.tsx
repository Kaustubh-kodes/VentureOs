import { Suspense } from "react";
import Navbar from "@/components/Navbar";
import AnalyseStrategyRoom from "@/components/AnalyseStrategyRoom";
import Footer from "@/components/Footer";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Analyse Your Startup — VentureOS Strategy Room",
  description:
    "Submit your startup idea and receive an evidence-based, AI-generated CEO venture strategy report.",
};

export default function AnalysePage() {
  return (
    <main className="min-h-screen bg-vo-black flex flex-col">
      <Navbar />
      <div className="flex-1 pt-16">
        <Suspense
          fallback={
            <div className="max-w-7xl mx-auto px-4 py-16 text-center text-vo-muted font-mono text-xs">
              INITIALIZING STRATEGY ROOM...
            </div>
          }
        >
          <AnalyseStrategyRoom />
        </Suspense>
      </div>
      <Footer />
    </main>
  );
}
