import React from 'react';

interface StatsCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  variant?: 'default' | 'danger' | 'warning' | 'success';
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
}) => {
  const borderStyles: Record<string, string> = {
    default: 'border-slate-800 bg-[#111827]/80 hover:border-slate-700',
    danger: 'border-red-900/30 bg-red-950/10 hover:border-red-800/40',
    warning: 'border-amber-900/30 bg-amber-950/10 hover:border-amber-800/40',
    success: 'border-emerald-900/30 bg-emerald-950/10 hover:border-emerald-800/40',
  };

  return (
    <div className={`p-5 rounded-xl border backdrop-blur-sm transition-all duration-200 ${borderStyles[variant]}`}>
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
        <div className="p-2 rounded-lg bg-slate-800/50 text-slate-300">{icon}</div>
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-white">{value}</span>
        {subtitle && <span className="text-xs text-slate-400">{subtitle}</span>}
      </div>
    </div>
  );
};
