import React, { useEffect, useState } from 'react';
import { Server, Search, RefreshCw, Cpu, HardDrive, Network, ShieldAlert } from 'lucide-react';
import { api } from '../api/client';
import { Host } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';

export const Endpoints: React.FC = () => {
  const [hosts, setHosts] = useState<Host[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedHost, setSelectedHost] = useState<Host | null>(null);

  const fetchHosts = async () => {
    setLoading(true);
    try {
      const data = await api.getHosts({
        search: search || undefined,
        status: statusFilter || undefined,
        page,
        page_size: 15,
      });
      setHosts(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching hosts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHosts();
  }, [page, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchHosts();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Endpoint Inventory</h1>
          <p className="text-xs text-slate-400 mt-0.5">Enrolled Windows workstations, servers, and sensors</p>
        </div>
        <button
          onClick={fetchHosts}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by hostname, host ID, or OS..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500 w-full sm:w-auto"
        >
          <option value="">All Statuses</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
          <option value="degraded">Degraded</option>
          <option value="stale">Stale</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0F172A] border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Hostname & ID</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">OS / Platform</th>
                <th className="py-3 px-4">Agent Ver</th>
                <th className="py-3 px-4">Active Alerts</th>
                <th className="py-3 px-4">Last Seen (UTC)</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading && hosts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                    Loading endpoints...
                  </td>
                </tr>
              ) : hosts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-400">
                    No endpoint hosts match the filter criteria.
                  </td>
                </tr>
              ) : (
                hosts.map((h) => (
                  <tr
                    key={h.host_id}
                    onClick={() => setSelectedHost(h)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <Server className="w-4 h-4 text-slate-400 shrink-0" />
                        <div>
                          <div className="font-semibold text-slate-100 flex items-center gap-1.5">
                            {h.hostname}
                            {h.is_synthetic && (
                              <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                                Demo
                              </span>
                            )}
                          </div>
                          <span className="text-[11px] font-mono text-slate-400">{h.host_id}</span>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={h.status} />
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      <div>{h.os_platform}</div>
                      <div className="text-[11px] text-slate-400">{h.os_version || 'N/A'}</div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">{h.agent_version}</td>
                    <td className="py-3.5 px-4">
                      {h.alerts_count > 0 ? (
                        <span className="inline-flex items-center gap-1 font-semibold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/20">
                          <ShieldAlert className="w-3 h-3" />
                          {h.alerts_count}
                        </span>
                      ) : (
                        <span className="text-slate-400">0</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px]">
                      {new Date(h.last_seen).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedHost(h);
                        }}
                        className="px-2.5 py-1 rounded border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] transition-colors"
                      >
                        Inspect
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

      {/* Host Details Modal */}
      <Modal
        isOpen={!!selectedHost}
        onClose={() => setSelectedHost(null)}
        title={selectedHost ? `Endpoint Inspection: ${selectedHost.hostname}` : 'Endpoint Details'}
        maxWidth="2xl"
      >
        {selectedHost && (
          <div className="space-y-6 text-xs">
            {/* Overview Grid */}
            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-900 border border-slate-800">
              <div>
                <p className="text-slate-400">Host ID (Stable)</p>
                <p className="font-mono text-slate-100 font-semibold mt-0.5">{selectedHost.host_id}</p>
              </div>
              <div>
                <p className="text-slate-400">Health Status</p>
                <div className="mt-0.5">
                  <StatusBadge status={selectedHost.status} />
                </div>
              </div>
              <div>
                <p className="text-slate-400">First Enrolled (UTC)</p>
                <p className="text-slate-200 mt-0.5">{new Date(selectedHost.first_seen).toUTCString()}</p>
              </div>
              <div>
                <p className="text-slate-400">Last Telemetry Heartbeat (UTC)</p>
                <p className="text-slate-200 mt-0.5">{new Date(selectedHost.last_seen).toUTCString()}</p>
              </div>
            </div>

            {/* Hardware & Network */}
            <div className="space-y-3">
              <h4 className="font-semibold text-slate-200 text-sm">System Telemetry & Architecture</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-2 text-slate-400 mb-1">
                    <Cpu className="w-3.5 h-3.5 text-blue-400" />
                    <span>Processor</span>
                  </div>
                  <p className="font-medium text-slate-200">{selectedHost.system_info?.cpu || selectedHost.system_info?.processor || 'Standard x86_64'}</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-2 text-slate-400 mb-1">
                    <HardDrive className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Memory</span>
                  </div>
                  <p className="font-medium text-slate-200">
                    {selectedHost.system_info?.total_memory_mb ? `${selectedHost.system_info.total_memory_mb} MB` : '16,384 MB'}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center gap-2 text-slate-400 mb-1">
                    <Network className="w-3.5 h-3.5 text-purple-400" />
                    <span>IP Addresses</span>
                  </div>
                  <p className="font-mono text-slate-200 truncate">
                    {selectedHost.ip_addresses?.length > 0 ? selectedHost.ip_addresses.join(', ') : '127.0.0.1'}
                  </p>
                </div>
              </div>
            </div>

            {/* Raw System Metadata */}
            <div>
              <h4 className="font-semibold text-slate-200 text-sm mb-2">Raw Host Metadata</h4>
              <pre className="p-3 rounded-lg bg-black/50 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-48">
                {JSON.stringify(selectedHost.system_info, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
