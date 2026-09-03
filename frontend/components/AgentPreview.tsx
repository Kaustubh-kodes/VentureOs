"use client";

interface AgentPreviewProps {
  number: string;
  name: string;
  description: string;
}

export default function AgentPreview({ number, name, description }: AgentPreviewProps) {
  return (
    <div className="group border border-vo-border bg-vo-dark p-6 hover:border-vo-red transition-all duration-200 hover:-translate-y-1 cursor-default">
      <div className="mb-4">
        <span className="text-vo-red text-xs font-bold tracking-widest">{number}</span>
      </div>
      <h3 className="text-vo-white text-sm font-black tracking-widest uppercase mb-3 group-hover:text-vo-white transition-colors">
        {name}
      </h3>
      <p className="text-vo-muted text-sm leading-relaxed">{description}</p>
      <div className="mt-4 w-0 h-px bg-vo-red group-hover:w-full transition-all duration-300" />
    </div>
  );
}
