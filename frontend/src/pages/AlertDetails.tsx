import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  ShieldAlert,
  FolderPlus,
  RefreshCw,
} from 'lucide-react';
import { api } from '../api/client';
import { Alert } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';

interface AlertDetailsProps {
  alertId: string;
  onBack: () => void;
  onNavigateToIncident?: (incidentId: string) => void;
}

export const AlertDetails: React.FC<AlertDetailsProps> = ({
  alertId,
  onBack,
  onNavigateToIncident,
}) => {
  const [alert, setAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  // False positive modal state
  const [fpModalOpen, setFpModalOpen] = useState(false);
  const [fpReason, setFpReason] = useState('');

  // Create incident modal state
  const [incModalOpen, setIncModalOpen] = useState(false);
  const [incTitle, setIncTitle] = useState('');
  const [incDescription, setIncDescription] = useState('');
  const [incSeverity, setIncSeverity] = useState('high');

  const fetchAlert = async () => {
    setLoading(true);
    try {
      const data = await api.getAlert(alertId);
      setAlert(data);
      setIncTitle(`Incident: ${data.title} on ${data.host_id}`);
      setIncDescription(`Investigation initiated from alert ${data.alert_id}.\n\nRule Rationale: ${data.description}`);
      setIncSeverity(data.severity);
    } catch (err) {
      console.error('Error fetching alert details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlert();
  }, [alertId]);

  const handleStatusChange = async (newStatus: string) => {
    if (newStatus === 'false_positive') {
      setFpModalOpen(true);
      return;
    }

    setActionLoading(true);
    try {
      const updated = await api.updateAlert(alertId, { status: newStatus });
      setAlert(updated);
    } catch (err: any) {
      console.error('Error updating alert status:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const submitFalsePositive = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fpReason.trim()) return;

    setActionLoading(true);
    try {
      const updated = await api.updateAlert(alertId, {
        status: 'false_positive',
        false_positive_reason: fpReason,
      });
      setAlert(updated);
      setFpModalOpen(false);
    } catch (err: any) {
      console.error('Error marking false positive:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      const newInc = await api.createIncident({
        title: incTitle,
        description: incDescription,
        severity: incSeverity,
        alert_ids: [alertId],
      });
      setIncModalOpen(false);
      await fetchAlert();
      if (onNavigateToIncident) {
        onNavigateToIncident(newInc.incident_id);
      }
    } catch (err: any) {
      console.error('Error creating incident from alert:', err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading || !alert) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
        <span>Loading alert investigation details...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top back button */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Alerts Queue</span>
      </button>

      {/* Main Alert Header Banner */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-[#111827] shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2.5">
            <SeverityBadge severity={alert.severity} />
            <StatusBadge status={alert.status} />
            <span className="font-mono text-xs font-semibold text-slate-300">{alert.alert_id}</span>
            {alert.is_synthetic && (
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                Demo
              </span>
            )}
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">{alert.title}</h1>
          <p className="text-xs text-slate-400 max-w-3xl">{alert.description}</p>
        </div>

        {/* Triage Actions */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          {alert.status === 'new' && (
            <button
              onClick={() => handleStatusChange('acknowledged')}
              disabled={actionLoading}
              className="px-3 py-1.5 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600/30 text-xs font-medium transition-colors"
            >
              Acknowledge
            </button>
          )}

          {alert.status !== 'investigating' && alert.status !== 'resolved' && (
            <button
              onClick={() => handleStatusChange('investigating')}
              disabled={actionLoading}
              className="px-3 py-1.5 rounded-lg bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 hover:bg-yellow-500/30 text-xs font-medium transition-colors"
            >
              Investigate
            </button>
          )}

          {alert.status !== 'resolved' && (
            <button
              onClick={() => handleStatusChange('resolved')}
              disabled={actionLoading}
              className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 text-xs font-medium transition-colors"
            >
              Resolve
            </button>
          )}

          {alert.status !== 'false_positive' && (
            <button
              onClick={() => setFpModalOpen(true)}
              disabled={actionLoading}
              className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 text-xs font-medium transition-colors"
            >
              False Positive
            </button>
          )}

          {!alert.incident_id && (
            <button
              onClick={() => setIncModalOpen(true)}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors"
            >
              <FolderPlus className="w-3.5 h-3.5" />
              <span>Create Incident</span>
            </button>
          )}
        </div>
      </div>

      {/* Linked Incident Alert Banner (if already part of incident) */}
      {alert.incident_id && (
        <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/40 flex items-center justify-between text-xs text-indigo-200">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-indigo-400" />
            <span>
              This alert is currently linked to security incident <strong className="font-mono text-white">{alert.incident_id}</strong>.
            </span>
          </div>
          {onNavigateToIncident && (
            <button
              onClick={() => onNavigateToIncident(alert.incident_id!)}
              className="px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-[11px] transition-colors"
            >
              View Incident
            </button>
          )}
        </div>
      )}

      {/* False Positive Rationale Banner (if marked FP) */}
      {alert.status === 'false_positive' && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <p className="font-semibold text-slate-300 mb-1">False Positive Justification:</p>
          <p className="text-slate-400 italic font-mono">{alert.false_positive_reason || 'No justification provided.'}</p>
        </div>
      )}

      {/* Metadata & MITRE Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Core Attributes */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#111827]/80 space-y-3 text-xs">
          <h3 className="font-semibold text-slate-200 text-sm border-b border-slate-800 pb-2">Target & Detection Context</h3>
          <div>
            <span className="text-slate-400">Endpoint Host:</span>
            <p className="font-mono text-slate-100 font-semibold mt-0.5">{alert.host_id}</p>
          </div>
          <div>
            <span className="text-slate-400">Triggering Rule:</span>
            <p className="font-mono text-blue-400 mt-0.5">{alert.rule_id}</p>
          </div>
          <div>
            <span className="text-slate-400">Aggregated Events:</span>
            <p className="text-slate-200 font-semibold mt-0.5">{alert.event_count} telemetry occurrences</p>
          </div>
          <div>
            <span className="text-slate-400">First Observed:</span>
            <p className="text-slate-300 mt-0.5">{new Date(alert.first_seen).toUTCString()}</p>
          </div>
          <div>
            <span className="text-slate-400">Last Observed:</span>
            <p className="text-slate-300 mt-0.5">{new Date(alert.last_seen).toUTCString()}</p>
          </div>
        </div>

        {/* MITRE ATT&CK Mapping */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#111827]/80 space-y-3 text-xs">
          <h3 className="font-semibold text-slate-200 text-sm border-b border-slate-800 pb-2">MITRE ATT&CK® Mapping</h3>
          {alert.mitre_technique_id ? (
            <>
              <div>
                <span className="text-slate-400">Technique ID:</span>
                <p className="font-mono text-base font-bold text-blue-400 mt-0.5">{alert.mitre_technique_id}</p>
              </div>
              <div>
                <span className="text-slate-400">Technique Name:</span>
                <p className="font-semibold text-slate-100 mt-0.5">{alert.mitre_technique_name}</p>
              </div>
              <div>
                <span className="text-slate-400">ATT&CK Tactic:</span>
                <p className="inline-block mt-1 px-2.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
                  {alert.mitre_tactic || 'Execution'}
                </p>
              </div>
            </>
          ) : (
            <p className="text-slate-400 italic">No MITRE ATT&CK technique mapped to this detection rule.</p>
          )}
        </div>

        {/* Assigned Analyst */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#111827]/80 space-y-3 text-xs">
          <h3 className="font-semibold text-slate-200 text-sm border-b border-slate-800 pb-2">Analyst Assignment</h3>
          <div>
            <span className="text-slate-400">Assigned Investigator:</span>
            <p className="font-semibold text-slate-200 mt-0.5">{alert.assigned_to || 'Unassigned'}</p>
          </div>
          <div>
            <span className="text-slate-400">Last Status Update:</span>
            <p className="text-slate-300 mt-0.5">{new Date(alert.updated_at).toUTCString()}</p>
          </div>
        </div>
      </div>

      {/* Evidence Summary Inspector */}
      <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-[#0F172A]">
          <h3 className="text-sm font-semibold text-slate-100">Preserved Forensic Evidence Summary</h3>
          <p className="text-xs text-slate-400">Attributes captured at detection time according to rule specifications</p>
        </div>
        <div className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
            {Object.entries(alert.evidence_summary || {}).map(([key, val]) => (
              <div key={key} className="p-3 rounded-lg bg-slate-900 border border-slate-800/80">
                <span className="text-slate-400 uppercase text-[10px] block mb-1 font-sans font-semibold">
                  {key.replace('_', ' ')}
                </span>
                <span className="text-slate-200 break-all">{typeof val === 'object' ? JSON.stringify(val) : String(val)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Linked Telemetry Events */}
      <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-[#0F172A] flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Associated Security Telemetry Events</h3>
            <p className="text-xs text-slate-400">Specific raw events that fulfilled the rule condition criteria</p>
          </div>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-xs font-mono font-semibold">
            {alert.events?.length || 0} events linked
          </span>
        </div>
        <div className="divide-y divide-slate-800/60 font-mono text-xs">
          {!alert.events || alert.events.length === 0 ? (
            <div className="p-6 text-center text-slate-400 font-sans">No detailed events linked.</div>
          ) : (
            alert.events.map((ev) => (
              <div key={ev.event_uuid} className="p-4 hover:bg-slate-800/30">
                <div className="flex items-center justify-between text-[11px] mb-1.5 font-sans">
                  <span className="font-semibold text-blue-400 uppercase tracking-wider">{ev.event_type}</span>
                  <span className="text-slate-400">{new Date(ev.timestamp).toUTCString()}</span>
                </div>
                <div className="text-slate-300">
                  {ev.process_name && (
                    <p>
                      <strong>Process:</strong> {ev.process_name} (PID: {ev.process_id})
                    </p>
                  )}
                  {ev.command_line && (
                    <p className="text-slate-400 text-[11px] mt-0.5 break-all">
                      <strong>CmdLine:</strong> {ev.command_line}
                    </p>
                  )}
                  {ev.network_remote_ip && (
                    <p>
                      <strong>Remote Socket:</strong> {ev.network_remote_ip}:{ev.network_remote_port} ({ev.network_protocol})
                    </p>
                  )}
                  {ev.file_path && (
                    <p>
                      <strong>File:</strong> {ev.file_action} - {ev.file_path}
                    </p>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* False Positive Modal */}
      <Modal
        isOpen={fpModalOpen}
        onClose={() => setFpModalOpen(false)}
        title="Mark Alert as False Positive"
      >
        <form onSubmit={submitFalsePositive} className="space-y-4 text-xs">
          <p className="text-slate-400">
            Please document the investigation rationale for why this detection does not represent malicious adversary activity.
          </p>
          <div>
            <label className="block font-medium text-slate-300 mb-1.5">False Positive Justification Reason</label>
            <textarea
              required
              rows={4}
              value={fpReason}
              onChange={(e) => setFpReason(e.target.value)}
              placeholder="e.g., Verified administrative script deployed by corporate SCCM team for software update..."
              className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setFpModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold"
            >
              Submit & Close Alert
            </button>
          </div>
        </form>
      </Modal>

      {/* Create Incident Modal */}
      <Modal
        isOpen={incModalOpen}
        onClose={() => setIncModalOpen(false)}
        title="Promote Alert to Security Incident"
        maxWidth="xl"
      >
        <form onSubmit={handleCreateIncident} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Incident Title</label>
            <input
              type="text"
              required
              value={incTitle}
              onChange={(e) => setIncTitle(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Incident Severity</label>
            <select
              value={incSeverity}
              onChange={(e) => setIncSeverity(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Description & Investigation Scope</label>
            <textarea
              required
              rows={4}
              value={incDescription}
              onChange={(e) => setIncDescription(e.target.value)}
              className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIncModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
            >
              Open Incident
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
