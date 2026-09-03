"use client";

interface FeatureCardProps {
  title: string;
  description: string;
  icon?: string;
}

export default function FeatureCard({ title, description, icon }: FeatureCardProps) {
  return (
    <div className="group border border-vo-border bg-vo-dark p-6 hover:border-vo-red transition-all duration-200 hover:-translate-y-1">
      {icon && (
        <div className="text-vo-red text-2xl mb-4" aria-hidden="true">
          {icon}
        </div>
      )}
      <h3 className="text-vo-white text-sm font-black tracking-widest uppercase mb-3">
        {title}
      </h3>
      <p className="text-vo-muted text-sm leading-relaxed">{description}</p>
    </div>
  );
}
