import React, { useEffect, useState } from 'react';
import { ShieldAlert, Plus, Search, RefreshCw, ChevronRight, MessageSquare } from 'lucide-react';
import { api } from '../api/client';
import { Incident } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';

interface IncidentsProps {
  onSelectIncident: (incidentId: string) => void;
}

export const Incidents: React.FC<IncidentsProps> = ({ onSelectIncident }) => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // New incident modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState('medium');
  const [creating, setCreating] = useState(false);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const data = await api.getIncidents({
        search: search || undefined,
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
        page,
        page_size: 15,
      });
      setIncidents(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [page, statusFilter, severityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchIncidents();
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const newInc = await api.createIncident({
        title,
        description,
        severity,
      });
      setCreateModalOpen(false);
      setTitle('');
      setDescription('');
      onSelectIncident(newInc.incident_id);
    } catch (err: any) {
      alert(err.message || 'Error creating incident');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Incident Management</h1>
          <p className="text-xs text-slate-400 mt-0.5">SOC case management, containment tracking, and timeline notes</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCreateModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Incident</span>
          </button>
          <button
            onClick={fetchIncidents}
            className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search incident title, description, ID..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="contained">Contained</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>

        <select
          value={severityFilter}
          onChange={(e) => {
            setSeverityFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Incidents Table */}
      <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0F172A] border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Incident Title & ID</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Assigned Analyst</th>
                <th className="py-3 px-4">Timeline Notes</th>
                <th className="py-3 px-4">Created At (UTC)</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading && incidents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                    Loading incidents...
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400">
                    No security incidents match the query criteria.
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr
                    key={inc.incident_id}
                    onClick={() => onSelectIncident(inc.incident_id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-4">
                      <SeverityBadge severity={inc.severity} />
                    </td>
                    <td className="py-3.5 px-4 max-w-md">
                      <div className="font-semibold text-slate-100 flex items-center gap-1.5 truncate">
                        {inc.title}
                        {inc.is_synthetic && (
                          <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                            Demo
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] font-mono text-slate-400">{inc.incident_id}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={inc.status} />
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-medium">{inc.assigned_to || 'Unassigned'}</td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1 text-slate-400">
                        <MessageSquare className="w-3.5 h-3.5" />
                        <span>{inc.investigation_notes?.length || 0}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px] whitespace-nowrap">
                      {new Date(inc.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectIncident(inc.incident_id);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-colors"
                      >
                        <span>Investigate</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <Pagination
          page={page}
          totalPages={totalPages}
          totalItems={total}
          onPageChange={setPage}
        />
      </div>

      {/* Create Incident Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Open New Security Incident"
        maxWidth="lg"
      >
        <form onSubmit={handleCreate} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Incident Title</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Compromised PowerShell execution on HR-WIN10"
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Initial Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Description & Scope</label>
            <textarea
              required
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe suspected attack vectors, targeted hosts, or observed telemetry..."
              className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setCreateModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold"
            >
              {creating ? 'Creating...' : 'Create Case'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
