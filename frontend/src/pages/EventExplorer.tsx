import React, { useEffect, useState } from 'react';
import { Search, Activity, RefreshCw, Terminal, Globe, FileText, HeartPulse } from 'lucide-react';
import { api } from '../api/client';
import { SecurityEvent } from '../types';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';

export const EventExplorer: React.FC = () => {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [eventTypeFilter, setEventTypeFilter] = useState('');
  const [hostIdFilter, setHostIdFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await api.getEvents({
        search: search || undefined,
        event_type: eventTypeFilter || undefined,
        host_id: hostIdFilter || undefined,
        page,
        page_size: 20,
      });
      setEvents(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [page, eventTypeFilter, hostIdFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchEvents();
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'process_creation':
        return <Terminal className="w-3.5 h-3.5 text-blue-400" />;
      case 'network_connection':
        return <Globe className="w-3.5 h-3.5 text-purple-400" />;
      case 'file_activity':
        return <FileText className="w-3.5 h-3.5 text-emerald-400" />;
      case 'agent_health':
        return <HeartPulse className="w-3.5 h-3.5 text-amber-400" />;
      default:
        return <Activity className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Event Explorer</h1>
          <p className="text-xs text-slate-400 mt-0.5">Normalized endpoint telemetry stream and forensic search</p>
        </div>
        <button
          onClick={fetchEvents}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <form onSubmit={handleSearchSubmit} className="sm:col-span-2 relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search command lines, paths, remote IPs, processes..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </form>

        <select
          value={eventTypeFilter}
          onChange={(e) => {
            setEventTypeFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Event Types</option>
          <option value="process_creation">Process Creation</option>
          <option value="network_connection">Network Connection</option>
          <option value="file_activity">File Activity</option>
          <option value="agent_health">Agent Health</option>
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
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Host</th>
                <th className="py-3 px-4">Primary Attribute / Command Line</th>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4 text-right">Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {loading && events.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-slate-400 font-sans">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                    Loading security events...
                  </td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-slate-400 font-sans">
                    No security events found.
                  </td>
                </tr>
              ) : (
                events.map((ev) => (
                  <tr
                    key={ev.event_uuid}
                    onClick={() => setSelectedEvent(ev)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                      {new Date(ev.timestamp).toISOString().replace('T', ' ').substring(0, 19)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[10px] uppercase font-sans">
                        {getEventIcon(ev.event_type)}
                        {ev.event_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{ev.host_id}</td>
                    <td className="py-3 px-4 text-slate-200 max-w-md truncate">
                      {ev.process_name && (
                        <span>
                          <strong className="text-blue-400">{ev.process_name}</strong>{' '}
                          <span className="text-slate-400">({ev.command_line || 'no cmdline'})</span>
                        </span>
                      )}
                      {ev.network_remote_ip && (
                        <span>
                          <strong className="text-purple-400">{ev.network_protocol?.toUpperCase() || 'TCP'}</strong>{' '}
                          {ev.network_remote_ip}:{ev.network_remote_port}
                        </span>
                      )}
                      {ev.file_path && (
                        <span>
                          <strong className="text-emerald-400">{ev.file_action || 'ACTION'}</strong> {ev.file_path}
                        </span>
                      )}
                      {ev.event_type === 'agent_health' && (
                        <span className="text-amber-400">
                          Status: {ev.data?.status} • Memory: {ev.data?.memory_usage_mb}MB
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{ev.username || 'SYSTEM'}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedEvent(ev);
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

      {/* Raw Event Modal */}
      <Modal
        isOpen={!!selectedEvent}
        onClose={() => setSelectedEvent(null)}
        title={selectedEvent ? `Event Inspection: ${selectedEvent.event_uuid}` : 'Event Inspection'}
        maxWidth="2xl"
      >
        {selectedEvent && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-xs p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div>
                <span className="text-slate-400">Event Type:</span>
                <p className="font-semibold text-blue-400 uppercase mt-0.5">{selectedEvent.event_type}</p>
              </div>
              <div>
                <span className="text-slate-400">Host ID:</span>
                <p className="font-mono text-slate-200 mt-0.5">{selectedEvent.host_id}</p>
              </div>
              <div>
                <span className="text-slate-400">Generated Timestamp (UTC):</span>
                <p className="text-slate-200 mt-0.5">{new Date(selectedEvent.timestamp).toUTCString()}</p>
              </div>
              <div>
                <span className="text-slate-400">Ingested At (UTC):</span>
                <p className="text-slate-200 mt-0.5">{new Date(selectedEvent.ingested_at).toUTCString()}</p>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-slate-200 mb-2">Raw Normalized Telemetry Payload</p>
              <pre className="p-4 rounded-xl bg-black/60 border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto max-h-96">
                {JSON.stringify(selectedEvent, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
