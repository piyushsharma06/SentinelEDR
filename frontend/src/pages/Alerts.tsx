import React, { useEffect, useState } from 'react';
import { AlertOctagon, Search, RefreshCw, ChevronRight, Filter } from 'lucide-react';
import { api } from '../api/client';
import { Alert } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { Pagination } from '../components/Pagination';

interface AlertsProps {
  onSelectAlert: (alertId: string) => void;
}

export const Alerts: React.FC<AlertsProps> = ({ onSelectAlert }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [hostIdFilter, setHostIdFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts({
        search: search || undefined,
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        host_id: hostIdFilter || undefined,
        page,
        page_size: 15,
      });
      setAlerts(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [page, severityFilter, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchAlerts();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Detection Alerts</h1>
          <p className="text-xs text-slate-400 mt-0.5">Automated detection rule matches and anomaly triage queue</p>
        </div>
        <button
          onClick={fetchAlerts}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filters Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <form onSubmit={handleSearchSubmit} className="sm:col-span-1 relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search alerts, hosts, rules..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>

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
          <option value="info">Info</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Triage Statuses</option>
          <option value="new">New</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
          <option value="false_positive">False Positive</option>
        </select>

        <input
          type="text"
          value={hostIdFilter}
          onChange={(e) => {
            setHostIdFilter(e.target.value);
            setPage(1);
          }}
          placeholder="Filter by Host ID..."
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0F172A] border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Alert Title & ID</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Host</th>
                <th className="py-3 px-4">MITRE ATT&CK</th>
                <th className="py-3 px-4">Events</th>
                <th className="py-3 px-4">Last Seen</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading && alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                    Loading alerts...
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-slate-400">
                    No detection alerts match the query.
                  </td>
                </tr>
              ) : (
                alerts.map((alt) => (
                  <tr
                    key={alt.alert_id}
                    onClick={() => onSelectAlert(alt.alert_id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-4">
                      <SeverityBadge severity={alt.severity} />
                    </td>
                    <td className="py-3.5 px-4 max-w-sm">
                      <div className="font-semibold text-slate-100 flex items-center gap-1.5 truncate">
                        {alt.title}
                        {alt.is_synthetic && (
                          <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                            Demo
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] font-mono text-slate-400">{alt.alert_id} • Rule: {alt.rule_id}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={alt.status} />
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">{alt.host_id}</td>
                    <td className="py-3.5 px-4">
                      {alt.mitre_technique_id ? (
                        <div className="space-y-0.5">
                          <span className="font-mono text-blue-400 font-semibold">{alt.mitre_technique_id}</span>
                          <p className="text-[10px] text-slate-400 truncate max-w-[140px]">{alt.mitre_technique_name}</p>
                        </div>
                      ) : (
                        <span className="text-slate-400 text-[11px]">N/A</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-300">{alt.event_count}</td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px] whitespace-nowrap">
                      {new Date(alt.last_seen).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectAlert(alt.alert_id);
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
    </div>
  );
};
