import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  ShieldAlert,
  Clock,
  User,
  Plus,
  Send,
  Link,
  Unlink,
  CheckCircle,
  RefreshCw,
  MessageSquare,
} from 'lucide-react';
import { api } from '../api/client';
import { Incident, Alert } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';

interface IncidentDetailsProps {
  incidentId: string;
  onBack: () => void;
  onSelectAlert: (alertId: string) => void;
}

export const IncidentDetails: React.FC<IncidentDetailsProps> = ({
  incidentId,
  onBack,
  onSelectAlert,
}) => {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  // Investigation note input
  const [newNote, setNewNote] = useState('');

  // Link Alert Modal
  const [linkModalOpen, setLinkModalOpen] = useState(false);
  const [availableAlerts, setAvailableAlerts] = useState<Alert[]>([]);
  const [selectedAlertToLink, setSelectedAlertToLink] = useState('');

  const fetchIncident = async () => {
    setLoading(true);
    try {
      const data = await api.getIncident(incidentId);
      setIncident(data);
    } catch (err) {
      console.error('Error fetching incident details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [incidentId]);

  const handleStatusChange = async (newStatus: string) => {
    setActionLoading(true);
    try {
      const updated = await api.updateIncident(incidentId, { status: newStatus });
      setIncident(updated);
    } catch (err: any) {
      console.error('Error updating incident status:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSeverityChange = async (newSeverity: string) => {
    setActionLoading(true);
    try {
      const updated = await api.updateIncident(incidentId, { severity: newSeverity });
      setIncident(updated);
    } catch (err: any) {
      console.error('Error updating severity:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    setActionLoading(true);
    try {
      const updated = await api.updateIncident(incidentId, { add_note: newNote });
      setIncident(updated);
      setNewNote('');
    } catch (err: any) {
      console.error('Error adding timeline note:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const openLinkModal = async () => {
    setLinkModalOpen(true);
    try {
      const data = await api.getAlerts({ page_size: 50 });
      // Filter out alerts already linked to this incident
      const unlinked = data.items.filter((a) => a.incident_id !== incidentId);
      setAvailableAlerts(unlinked);
      if (unlinked.length > 0) {
        setSelectedAlertToLink(unlinked[0].alert_id);
      }
    } catch (err) {
      console.error('Error fetching unlinked alerts:', err);
    }
  };

  const handleLinkAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAlertToLink) return;

    setActionLoading(true);
    try {
      const updated = await api.updateIncident(incidentId, {
        link_alert_ids: [selectedAlertToLink],
      });
      setIncident(updated);
      setLinkModalOpen(false);
    } catch (err: any) {
      console.error('Error linking alert to incident:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnlinkAlert = async (alertIdToUnlink: string) => {
    setActionLoading(true);
    try {
      const updated = await api.updateIncident(incidentId, {
        unlink_alert_ids: [alertIdToUnlink],
      });
      setIncident(updated);
    } catch (err: any) {
      console.error('Error unlinking alert:', err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading || !incident) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
        <span>Loading incident investigation console...</span>
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
        <span>Back to Incident Management</span>
      </button>

      {/* Main Header Banner */}
      <div className="p-6 rounded-2xl border border-slate-800 bg-[#111827] shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2.5">
            <SeverityBadge severity={incident.severity} />
            <StatusBadge status={incident.status} />
            <span className="font-mono text-xs font-semibold text-slate-300">{incident.incident_id}</span>
            {incident.is_synthetic && (
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                Demo
              </span>
            )}
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">{incident.title}</h1>
          <p className="text-xs text-slate-400 max-w-3xl">{incident.description}</p>
        </div>

        {/* Quick Lifecycle Controls */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <select
            value={incident.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            disabled={actionLoading}
            className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 font-medium focus:outline-none focus:border-blue-500"
          >
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="contained">Contained</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>

          <select
            value={incident.severity}
            onChange={(e) => handleSeverityChange(e.target.value)}
            disabled={actionLoading}
            className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 font-medium focus:outline-none focus:border-blue-500"
          >
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Timeline & Investigation Notes */}
        <div className="lg:col-span-2 space-y-6">
          {/* Notes Timeline Box */}
          <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden shadow-sm">
            <div className="p-4 border-b border-slate-800 bg-[#0F172A] flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
                <MessageSquare className="w-4 h-4 text-blue-400" />
                <span>Investigation Activity & Notes Log</span>
              </div>
              <span className="text-xs text-slate-400">{incident.investigation_notes?.length || 0} entries</span>
            </div>

            {/* Notes List */}
            <div className="p-6 space-y-4 max-h-[460px] overflow-y-auto">
              {!incident.investigation_notes || incident.investigation_notes.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No notes added to this investigation yet.</p>
              ) : (
                incident.investigation_notes.map((note, index) => (
                  <div key={note.id || index} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-blue-400 flex items-center gap-1.5">
                        <User className="w-3 h-3 text-slate-400" />
                        {note.author}
                      </span>
                      <span className="text-slate-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(note.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">{note.text}</p>
                  </div>
                ))
              )}
            </div>

            {/* Note Input */}
            <form onSubmit={handleAddNote} className="p-4 border-t border-slate-800 bg-slate-900/40 flex gap-2">
              <input
                type="text"
                required
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Log an observation, containment step, or IOC..."
                className="flex-1 px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
              <button
                type="submit"
                disabled={actionLoading || !newNote.trim()}
                className="inline-flex items-center gap-1 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Post Note</span>
              </button>
            </form>
          </div>

          {/* Linked Detections / Alerts Section */}
          <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden shadow-sm">
            <div className="p-4 border-b border-slate-800 bg-[#0F172A] flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-100">Linked Threat Detections</h3>
                <p className="text-xs text-slate-400">Security alerts contributing evidence to this incident case</p>
              </div>
              <button
                onClick={openLinkModal}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
              >
                <Link className="w-3.5 h-3.5" />
                <span>Link Alert</span>
              </button>
            </div>

            <div className="divide-y divide-slate-800/60">
              {!incident.alerts || incident.alerts.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400">
                  No alerts currently linked to this incident. Click "Link Alert" to attach detections.
                </div>
              ) : (
                incident.alerts.map((alt) => (
                  <div
                    key={alt.alert_id}
                    className="p-4 hover:bg-slate-800/30 flex items-center justify-between gap-4 text-xs"
                  >
                    <div
                      onClick={() => onSelectAlert(alt.alert_id)}
                      className="cursor-pointer space-y-1 min-w-0 flex-1"
                    >
                      <div className="flex items-center gap-2">
                        <SeverityBadge severity={alt.severity} size="sm" />
                        <span className="font-semibold text-slate-200 truncate">{alt.title}</span>
                      </div>
                      <p className="text-[11px] font-mono text-slate-400">
                        {alt.alert_id} • Host: {alt.host_id} • Rule: {alt.rule_id}
                      </p>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <StatusBadge status={alt.status} />
                      <button
                        onClick={() => handleUnlinkAlert(alt.alert_id)}
                        disabled={actionLoading}
                        title="Unlink alert from incident"
                        className="p-1 rounded text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-colors"
                      >
                        <Unlink className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Case Metadata & Assignment */}
        <div className="space-y-6">
          <div className="p-5 rounded-xl border border-slate-800 bg-[#111827]/80 text-xs space-y-4">
            <h3 className="font-semibold text-slate-200 text-sm border-b border-slate-800 pb-2">Case Properties</h3>
            <div>
              <span className="text-slate-400">Case ID:</span>
              <p className="font-mono text-slate-100 font-semibold mt-0.5">{incident.incident_id}</p>
            </div>
            <div>
              <span className="text-slate-400">Investigator:</span>
              <p className="font-semibold text-slate-200 mt-0.5">{incident.assigned_to || 'Unassigned'}</p>
            </div>
            <div>
              <span className="text-slate-400">Lifecycle Status:</span>
              <div className="mt-1">
                <StatusBadge status={incident.status} />
              </div>
            </div>
            <div>
              <span className="text-slate-400">Creation Date (UTC):</span>
              <p className="text-slate-300 mt-0.5">{new Date(incident.created_at).toUTCString()}</p>
            </div>
            <div>
              <span className="text-slate-400">Last Modified (UTC):</span>
              <p className="text-slate-300 mt-0.5">{new Date(incident.updated_at).toUTCString()}</p>
            </div>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-[#111827]/80 text-xs space-y-3">
            <h3 className="font-semibold text-slate-200 text-sm border-b border-slate-800 pb-2">Investigation Guidance</h3>
            <p className="text-slate-400 leading-relaxed">
              When triaging an incident, document every observed artifact in the notes timeline:
            </p>
            <ul className="list-disc list-inside text-slate-300 space-y-1">
              <li>Process ancestry & command lines</li>
              <li>Outbound socket addresses and ports</li>
              <li>Attributed MITRE ATT&CK techniques</li>
              <li>Network containment verification</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Link Alert Modal */}
      <Modal
        isOpen={linkModalOpen}
        onClose={() => setLinkModalOpen(false)}
        title="Link Threat Detection Alert to Incident"
        maxWidth="lg"
      >
        <form onSubmit={handleLinkAlert} className="space-y-4 text-xs">
          <p className="text-slate-400">
            Select an active detection alert to associate its evidence and telemetry with this case.
          </p>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Select Alert</label>
            {availableAlerts.length === 0 ? (
              <p className="p-3 rounded-lg bg-slate-900 text-slate-400 italic">No unlinked alerts available.</p>
            ) : (
              <select
                value={selectedAlertToLink}
                onChange={(e) => setSelectedAlertToLink(e.target.value)}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
              >
                {availableAlerts.map((a) => (
                  <option key={a.alert_id} value={a.alert_id}>
                    [{a.severity.toUpperCase()}] {a.alert_id} — {a.title} ({a.host_id})
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setLinkModalOpen(false)}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={actionLoading || availableAlerts.length === 0}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold"
            >
              Link to Case
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
