import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import AgentPreview from "@/components/AgentPreview";
import FeatureCard from "@/components/FeatureCard";
import Footer from "@/components/Footer";
import Link from "next/link";

const AGENTS = [
  { number: "01", name: "CEO & STRATEGY", description: "Defines vision, mission, business model, revenue streams and 90-day strategic priorities." },
  { number: "02", name: "MARKET RESEARCH", description: "Analyses target customers, competitors, market size, trends and key opportunities." },
  { number: "03", name: "PRODUCT", description: "Defines the core product, MVP features, user flows and technical requirements." },
  { number: "04", name: "MARKETING & GROWTH", description: "Builds positioning, customer personas, acquisition channels and launch strategy." },
  { number: "05", name: "FINANCE", description: "Estimates startup costs, operating expenses, revenue assumptions and financial risks." },
  { number: "06", name: "TECHNICAL FEASIBILITY", description: "Assesses technical complexity, recommended stack, build timeline and engineering risks." },
  { number: "07", name: "SKEPTIC & RISK", description: "Challenges assumptions, identifies weaknesses, surfaces blind spots and key risks." },
  { number: "08", name: "INVESTMENT ANALYST", description: "Evaluates investment potential, scores the startup and provides an investment decision." },
];

const CAPABILITIES = [
  { icon: "⬡", title: "MULTI-AGENT INTELLIGENCE", description: "Multiple specialised AI agents analyse the same problem from distinct professional perspectives." },
  { icon: "◈", title: "EVIDENCE-AWARE RAG", description: "Relevant founder documents and knowledge are retrieved semantically when agents need context." },
  { icon: "◉", title: "PERSISTENT MEMORY", description: "Relevant startup history is retrieved across sessions — the system learns what you've already explored." },
  { icon: "◎", title: "RISK ANALYSIS", description: "A dedicated Skeptic Agent challenges every assumption and identifies weaknesses in the strategy." },
  { icon: "◆", title: "INVESTMENT INTELLIGENCE", description: "The Investment Analyst evaluates startup potential and generates a scored investment decision." },
  { icon: "◐", title: "LIVE STRATEGY SESSIONS", description: "Future versions will stream live agent activity and findings directly to your dashboard." },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-vo-black">
      <Navbar />
      <Hero />

      {/* Introduction */}
      <section className="bg-vo-dark border-t border-vo-border py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-start">
            <div>
              <p className="text-vo-red text-xs font-bold tracking-[0.25em] uppercase mb-4">About</p>
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-none tracking-tight text-vo-white">
                ONE IDEA.
                <br />
                MULTIPLE
                <br />
                PERSPECTIVES.
              </h2>
            </div>
            <div className="flex flex-col gap-6 pt-2">
              <p className="text-vo-muted text-lg leading-relaxed">
                VentureOS is not a single chatbot that generates a generic business plan.
              </p>
              <p className="text-vo-muted leading-relaxed">
                It runs a coordinated team of specialised AI agents — each with a distinct role, perspective, and
                set of responsibilities. They analyse your startup idea from different angles, challenge each
                other&apos;s assumptions, and combine their findings into a single structured venture strategy.
              </p>
              <p className="text-vo-muted leading-relaxed">
                The result is not an optimistic summary. It is a grounded, multi-perspective analysis designed
                to surface what is strong, what is weak, and what needs to be addressed before you build.
              </p>
              <div className="pt-2">
                <Link
                  href="/analyse"
                  className="inline-block bg-vo-red text-white font-black px-6 py-3 text-xs tracking-widest uppercase hover:bg-vo-red-hover transition-colors duration-200"
                >
                  Start Your Analysis
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Agents */}
      <section id="agents" className="bg-vo-black border-t border-vo-border py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-16">
            <p className="text-vo-red text-xs font-bold tracking-[0.25em] uppercase mb-4">The Team</p>
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-none tracking-tight text-vo-white">
              THE AGENTS
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {AGENTS.map((agent) => (
              <AgentPreview
                key={agent.number}
                number={agent.number}
                name={agent.name}
                description={agent.description}
              />
            ))}
          </div>
        </div>
      </section>

      <HowItWorks />

      {/* Capabilities */}
      <section id="capabilities" className="bg-vo-dark border-t border-vo-border py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-16">
            <p className="text-vo-red text-xs font-bold tracking-[0.25em] uppercase mb-4">Technology</p>
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-none tracking-tight text-vo-white">
              CAPABILITIES
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {CAPABILITIES.map((cap) => (
              <FeatureCard
                key={cap.title}
                icon={cap.icon}
                title={cap.title}
                description={cap.description}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-vo-black border-t border-vo-border py-24 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-vo-red text-xs font-bold tracking-[0.25em] uppercase mb-6">Get Started</p>
          <h2 className="text-4xl sm:text-5xl lg:text-7xl font-black leading-none tracking-tight text-vo-white mb-6">
            READY TO PUT
            <br />
            YOUR IDEA TO
            <br />
            THE TEST?
          </h2>
          <p className="text-vo-muted text-lg mb-10 max-w-lg mx-auto">
            Bring your startup idea into the strategy room.
          </p>
          <Link
            href="/analyse"
            className="inline-block bg-vo-red text-white font-black px-10 py-5 text-sm tracking-widest uppercase hover:bg-vo-red-hover transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-vo-red"
          >
            START ANALYSIS
          </Link>
        </div>
      </section>

      <Footer />
    </main>
  );
}
