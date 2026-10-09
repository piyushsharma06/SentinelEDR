import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface DemoBannerProps {
  show?: boolean;
}

export const DemoBanner: React.FC<DemoBannerProps> = ({ show = true }) => {
  if (!show) return null;

  return (
    <div className="bg-gradient-to-r from-amber-950 via-amber-900 to-amber-950 border-b border-amber-600/40 text-amber-200 px-4 py-1.5 text-xs font-semibold flex items-center justify-center gap-2 tracking-wide uppercase shadow-inner z-50">
      <AlertTriangle className="w-4 h-4 text-amber-400 animate-pulse" />
      <span>DEMO MODE ACTIVE — SYNTHETIC SECURITY TELEMETRY FOR EDUCATIONAL DEMONSTRATION</span>
      <span className="hidden md:inline text-amber-400/80 font-normal lowercase">(no live malware or destructive actions executed)</span>
    </div>
  );
};
