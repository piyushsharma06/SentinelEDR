import React, { useEffect, useState } from 'react';
import { ScrollText, Search, RefreshCw, User, Shield } from 'lucide-react';
import { api } from '../api/client';
import { AuditLog } from '../types';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [actorFilter, setActorFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [resourceFilter, setResourceFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs({
        actor: actorFilter || undefined,
        action: actionFilter || undefined,
        resource_type: resourceFilter || undefined,
        page,
        page_size: 20,
      });
      setLogs(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter, resourceFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Governance & Audit Logs</h1>
          <p className="text-xs text-slate-400 mt-0.5">Immutable audit trail of analyst and administrative actions</p>
        </div>
        <button
          onClick={fetchLogs}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            placeholder="Filter by actor username..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>

        <select
          value={actionFilter}
          onChange={(e) => {
            setActionFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Actions</option>
          <option value="auth.login">auth.login</option>
          <option value="alert.update">alert.update</option>
          <option value="incident.create">incident.create</option>
          <option value="incident.update">incident.update</option>
          <option value="rule.toggle">rule.toggle</option>
          <option value="agent.enrolled">agent.enrolled</option>
          <option value="demo.seeded">demo.seeded</option>
        </select>

        <select
          value={resourceFilter}
          onChange={(e) => {
            setResourceFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Resource Types</option>
          <option value="alert">Alerts</option>
          <option value="incident">Incidents</option>
          <option value="rule">Rules</option>
          <option value="auth">Auth</option>
          <option value="agent_credential">Agent Credential</option>
          <option value="system">System</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0F172A] border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Resource Target</th>
                <th className="py-3 px-4">Client IP</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {loading && logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-slate-400 font-sans">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                    Loading audit trail...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-slate-400 font-sans">
                    No audit records match the criteria.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr
                    key={log.id}
                    onClick={() => setSelectedLog(log)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                      {new Date(log.timestamp).toISOString().replace('T', ' ').substring(0, 19)}
                    </td>
                    <td className="py-3 px-4 text-blue-400 font-sans font-semibold">
                      <span className="flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5 text-slate-400" />
                        {log.actor_username}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 text-[10px]">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      <span className="text-slate-400">{log.resource_type}:</span> {log.resource_id || 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{log.ip_address || '127.0.0.1'}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLog(log);
                        }}
                        className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 text-[10px] font-sans"
                      >
                        JSON
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

      {/* Audit Log Modal */}
      <Modal
        isOpen={!!selectedLog}
        onClose={() => setSelectedLog(null)}
        title={selectedLog ? `Audit Record #${selectedLog.id}` : 'Audit Record'}
        maxWidth="lg"
      >
        {selectedLog && (
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div>
                <span className="text-slate-400">Actor Identity:</span>
                <p className="font-semibold text-blue-400 mt-0.5">{selectedLog.actor_username}</p>
              </div>
              <div>
                <span className="text-slate-400">Action:</span>
                <p className="font-mono text-slate-200 mt-0.5">{selectedLog.action}</p>
              </div>
              <div>
                <span className="text-slate-400">Target Resource:</span>
                <p className="font-mono text-slate-200 mt-0.5">{selectedLog.resource_type} ({selectedLog.resource_id})</p>
              </div>
              <div>
                <span className="text-slate-400">Timestamp (UTC):</span>
                <p className="text-slate-300 mt-0.5">{new Date(selectedLog.timestamp).toUTCString()}</p>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-slate-200 mb-1.5">Action Details & State Changes</p>
              <pre className="p-3.5 rounded-xl bg-black/60 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-60">
                {JSON.stringify(selectedLog.details, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
