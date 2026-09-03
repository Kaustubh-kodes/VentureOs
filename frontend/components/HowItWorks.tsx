export default function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "SUBMIT",
      description: "Tell VentureOS about your startup idea, target audience, industry, and available resources.",
    },
    {
      number: "02",
      title: "CONTEXT",
      description: "The system prepares the startup context and retrieves relevant knowledge from the knowledge base.",
    },
    {
      number: "03",
      title: "ANALYSE",
      description: "Specialised AI agents examine the idea from different perspectives — CEO, market, product, finance, and more.",
    },
    {
      number: "04",
      title: "CHALLENGE",
      description: "The Skeptic Agent identifies weaknesses, challenges assumptions, and surfaces potential risks.",
    },
    {
      number: "05",
      title: "STRATEGISE",
      description: "Insights are synthesised into an actionable startup strategy with 30 and 90-day roadmaps.",
    },
  ];

  return (
    <section id="how-it-works" className="bg-vo-black border-t border-vo-border py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-16">
          <p className="text-vo-red text-xs font-bold tracking-[0.25em] uppercase mb-4">Process</p>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-none tracking-tight text-vo-white">
            HOW IT WORKS
          </h2>
        </div>

        <div className="space-y-0">
          {steps.map((step, idx) => (
            <div
              key={step.number}
              className="group grid md:grid-cols-12 gap-4 md:gap-8 border-t border-vo-border py-8 hover:bg-vo-dark transition-colors duration-200 px-2"
            >
              <div className="md:col-span-1">
                <span className="text-vo-red text-xs font-bold tracking-widest">{step.number}</span>
              </div>
              <div className="md:col-span-3">
                <h3 className="text-vo-white text-xl font-black tracking-widest uppercase group-hover:text-vo-red transition-colors duration-200">
                  {step.title}
                </h3>
              </div>
              <div className="md:col-span-7">
                <p className="text-vo-muted leading-relaxed">{step.description}</p>
              </div>
              <div className="md:col-span-1 hidden md:flex items-center justify-end">
                {idx < steps.length - 1 && (
                  <span className="text-vo-border group-hover:text-vo-red transition-colors duration-200">v</span>
                )}
              </div>
            </div>
          ))}
          <div className="border-t border-vo-border" />
        </div>
      </div>
    </section>
  );
}
