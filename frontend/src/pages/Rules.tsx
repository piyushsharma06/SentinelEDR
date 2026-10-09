import React, { useEffect, useState } from 'react';
import { FileCode, Shield, Check, X, Info, RefreshCw, Eye } from 'lucide-react';
import { api } from '../api/client';
import { DetectionRule } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { Modal } from '../components/Modal';
import { useAuth } from '../context/AuthContext';

export const Rules: React.FC = () => {
  const { user } = useAuth();
  const [rules, setRules] = useState<DetectionRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRule, setSelectedRule] = useState<DetectionRule | null>(null);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');

  const fetchRules = async () => {
    setLoading(true);
    try {
      const data = await api.getRules({
        category: categoryFilter || undefined,
        severity: severityFilter || undefined,
      });
      setRules(data);
    } catch (err) {
      console.error('Error fetching detection rules:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, [categoryFilter, severityFilter]);

  const handleToggle = async (rule: DetectionRule, e: React.MouseEvent) => {
    e.stopPropagation();
    if (user?.role !== 'admin') {
      alert('Only administrators can toggle detection rule enforcement.');
      return;
    }

    try {
      const updated = await api.toggleRule(rule.rule_id, !rule.enabled);
      setRules((prev) => prev.map((r) => (r.rule_id === updated.rule_id ? updated : r)));
    } catch (err: any) {
      alert(err.message || 'Error toggling rule');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">YAML Detection Engine Rules</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Testable heuristics, MITRE ATT&CK® mappings, and behavioral telemetry logic
          </p>
        </div>
        <button
          onClick={fetchRules}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Reload Catalog</span>
        </button>
      </div>

      {/* Educational Notice Banner */}
      <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-500/30 flex items-start gap-3 text-xs text-blue-200">
        <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong>Educational Detection Note:</strong> Detection rules represent hypothesis-driven telemetry signatures and heuristics. A matched rule indicates observable behavior aligning with an adversary technique—not definitive forensic proof of compromise. Every detection requires analyst verification against environment context.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Categories</option>
          <option value="Execution">Execution</option>
          <option value="Defense Evasion">Defense Evasion</option>
          <option value="Command and Control">Command and Control</option>
          <option value="Impact / Persistence">Impact / Persistence</option>
          <option value="Defense Evasion / System Integrity">System Integrity</option>
        </select>
      </div>

      {/* Rules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-2 text-center py-12 text-slate-400 text-xs">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
            Loading detection rules...
          </div>
        ) : rules.length === 0 ? (
          <div className="col-span-2 text-center py-12 text-slate-400 text-xs">
            No rules matched the filter criteria.
          </div>
        ) : (
          rules.map((r) => (
            <div
              key={r.rule_id}
              onClick={() => setSelectedRule(r)}
              className="p-5 rounded-xl border border-slate-800 bg-[#111827]/80 hover:border-slate-700 cursor-pointer transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={r.severity} size="sm" />
                    <span className="text-[11px] font-mono text-slate-400">{r.rule_id}</span>
                  </div>
                  <button
                    onClick={(e) => handleToggle(r, e)}
                    title={user?.role === 'admin' ? 'Toggle rule active state' : 'Administrator required to toggle'}
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border transition-colors ${
                      r.enabled
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
                    }`}
                  >
                    {r.enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>

                <h3 className="font-semibold text-slate-100 text-sm">{r.name}</h3>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{r.description}</p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                {r.mitre_technique_id ? (
                  <span className="font-mono text-[11px] text-blue-400 font-semibold flex items-center gap-1">
                    <Shield className="w-3.5 h-3.5" />
                    {r.mitre_technique_id} • {r.mitre_technique_name}
                  </span>
                ) : (
                  <span className="text-slate-400 text-[11px]">General Sensor</span>
                )}
                <span className="text-[11px] text-slate-400 font-mono">v{r.version}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Rule Inspection Modal */}
      <Modal
        isOpen={!!selectedRule}
        onClose={() => setSelectedRule(null)}
        title={selectedRule ? `Detection Logic: ${selectedRule.rule_id}` : 'Rule Logic'}
        maxWidth="2xl"
      >
        {selectedRule && (
          <div className="space-y-5 text-xs">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <SeverityBadge severity={selectedRule.severity} />
                <span className="font-semibold text-slate-100 text-base">{selectedRule.name}</span>
              </div>
              <p className="text-slate-300 leading-relaxed">{selectedRule.description}</p>
            </div>

            {/* MITRE Info */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <h4 className="font-semibold text-slate-200">MITRE ATT&CK Classification</h4>
              {selectedRule.mitre_technique_id ? (
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <span className="text-slate-400">Technique ID</span>
                    <p className="font-mono text-blue-400 font-bold mt-0.5">{selectedRule.mitre_technique_id}</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Technique Name</span>
                    <p className="text-slate-200 font-medium mt-0.5">{selectedRule.mitre_technique_name}</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Tactic</span>
                    <p className="text-slate-200 font-medium mt-0.5">{selectedRule.mitre_tactic}</p>
                  </div>
                </div>
              ) : (
                <p className="text-slate-400 italic">No formal ATT&CK mapping assigned.</p>
              )}
            </div>

            {/* Rationale & False Positives */}
            {selectedRule.rationale && (
              <div>
                <h4 className="font-semibold text-slate-200 mb-1">Threat Rationale & Intent</h4>
                <p className="text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800 leading-relaxed whitespace-pre-line">
                  {selectedRule.rationale}
                </p>
              </div>
            )}

            {selectedRule.false_positive_notes && (
              <div>
                <h4 className="font-semibold text-amber-300 mb-1">Common False Positive Scenarios</h4>
                <p className="text-slate-300 bg-amber-950/10 p-3 rounded-lg border border-amber-900/30 leading-relaxed whitespace-pre-line">
                  {selectedRule.false_positive_notes}
                </p>
              </div>
            )}

            {/* Condition Definition */}
            <div>
              <h4 className="font-semibold text-slate-200 mb-1">Evaluation Condition Criteria</h4>
              <pre className="p-3.5 rounded-xl bg-black/60 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-52">
                {JSON.stringify(selectedRule.conditions, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
