import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const stat = (status || 'unknown').toLowerCase();

  const styles: Record<string, string> = {
    // Alerts
    new: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
    acknowledged: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
    investigating: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
    resolved: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    false_positive: 'bg-slate-500/15 text-slate-400 border-slate-500/30',

    // Incidents
    open: 'bg-red-500/15 text-red-400 border-red-500/30',
    contained: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
    closed: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',

    // Hosts
    online: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    offline: 'bg-slate-600/15 text-slate-400 border-slate-600/30',
    degraded: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    stale: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
  };

  const currentStyle = styles[stat] || 'bg-slate-700/30 text-slate-300 border-slate-600/30';
  const label = stat.replace('_', ' ');

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium uppercase tracking-wider border ${currentStyle}`}>
      {label}
    </span>
  );
};
