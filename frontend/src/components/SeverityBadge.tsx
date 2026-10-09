import React from 'react';

interface SeverityBadgeProps {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info' | string;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const sev = (severity || 'info').toLowerCase();

  const styles: Record<string, string> = {
    critical: 'bg-red-500/15 text-red-400 border-red-500/30',
    high: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
    medium: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    low: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    info: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  };

  const currentStyle = styles[sev] || styles.info;
  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-semibold';

  return (
    <span className={`inline-flex items-center uppercase tracking-wider rounded border ${padding} ${currentStyle}`}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-80" />
      {sev}
    </span>
  );
};
