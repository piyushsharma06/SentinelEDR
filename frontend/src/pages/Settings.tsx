import React, { useState } from 'react';
import { Settings as SettingsIcon, Terminal, Copy, Check, ShieldCheck, Key, BookOpen } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Settings: React.FC = () => {
  const { user } = useAuth();
  const [copiedToken, setCopiedToken] = useState(false);
  const [copiedCommand, setCopiedCommand] = useState(false);

  const enrollmentToken = 'sentinel-agent-enrollment-secret-key-change-me';
  const startAgentCommand = 'python -m sentinel_agent.main --config agent/config.yaml';

  const copyToClipboard = (text: string, setCopied: (v: boolean) => void) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white">Agent Setup & Configuration</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Deploy and configure endpoint telemetry collectors for Windows 10/11
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Windows Agent Deployment Guide */}
        <div className="p-6 rounded-xl border border-slate-800 bg-[#111827]/80 space-y-5 text-xs">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100 border-b border-slate-800 pb-3">
            <Terminal className="w-4 h-4 text-blue-400" />
            <span>Windows Endpoint Agent Deployment</span>
          </div>

          <p className="text-slate-300 leading-relaxed">
            The SentinelEDR agent collects safe, non-invasive process and network connection telemetry on Windows hosts. Follow these steps to configure and launch an agent instance:
          </p>

          <div className="space-y-3 font-sans">
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-slate-200">1. Install Dependencies</span>
              <p className="text-slate-400 font-mono text-[11px]">
                pip install -r agent/requirements.txt
              </p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-slate-200">2. Pre-Shared Enrollment Token</span>
              <div className="flex items-center justify-between gap-2 bg-black/40 p-2 rounded border border-slate-800 font-mono text-[11px] text-blue-400">
                <span className="truncate">{enrollmentToken}</span>
                <button
                  onClick={() => copyToClipboard(enrollmentToken, setCopiedToken)}
                  className="p-1 hover:text-white transition-colors"
                  title="Copy enrollment token"
                >
                  {copiedToken ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-slate-200">3. Run Agent Daemon</span>
              <div className="flex items-center justify-between gap-2 bg-black/40 p-2 rounded border border-slate-800 font-mono text-[11px] text-emerald-400">
                <span className="truncate">{startAgentCommand}</span>
                <button
                  onClick={() => copyToClipboard(startAgentCommand, setCopiedCommand)}
                  className="p-1 hover:text-white transition-colors"
                  title="Copy start command"
                >
                  {copiedCommand ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Security & Privacy Boundaries */}
        <div className="p-6 rounded-xl border border-slate-800 bg-[#111827]/80 space-y-5 text-xs">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100 border-b border-slate-800 pb-3">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Educational Safety & Privacy Guarantee</span>
          </div>

          <p className="text-slate-300 leading-relaxed">
            SentinelEDR is purposefully engineered for cybersecurity training and blue-team analysis. It enforces strict privacy boundaries:
          </p>

          <ul className="space-y-2.5 text-slate-300">
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>No Keylogging or Content Inspection:</strong> Keystrokes, passwords, clipboard contents, and browser sessions are never monitored.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>Zero File Uploads:</strong> The agent never uploads raw document or binary contents to the backend server.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>No Remote Code Execution:</strong> The agent does not accept arbitrary remote commands or execution instructions from the central server.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>Opt-In Monitored Directory:</strong> File activity collection is restricted exclusively to an explicitly designated demonstration directory.
              </span>
            </li>
          </ul>

          <div className="pt-2 border-t border-slate-800/80">
            <div className="flex items-center justify-between text-slate-400 text-[11px]">
              <span>Active Session User</span>
              <span className="font-semibold text-slate-200">{user?.username} ({user?.role})</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
