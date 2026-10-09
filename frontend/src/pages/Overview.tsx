import React, { useEffect, useState } from 'react';
import {
  Server,
  Activity,
  AlertOctagon,
  ShieldAlert,
  Clock,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { api } from '../api/client';
import { DashboardStats, Alert, SecurityEvent } from '../types';
import { StatsCard } from '../components/StatsCard';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';

interface OverviewProps {
  onSelectAlert: (alertId: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const Overview: React.FC<OverviewProps> = ({ onSelectAlert, onNavigateTab }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [recentEvents, setRecentEvents] = useState<SecurityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [statsData, alertsData, eventsData] = await Promise.all([
        api.getStats(),
        api.getAlerts({ page: 1, page_size: 5 }),
        api.getEvents({ page: 1, page_size: 6 }),
      ]);
      setStats(statsData);
      setRecentAlerts(alertsData.items);
      setRecentEvents(eventsData.items);
    } catch (err) {
      console.error('Error fetching dashboard statistics:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleManualRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
        <span>Loading SOC Overview Telemetry...</span>
      </div>
    );
  }

  const severityChartData = stats
    ? [
        { name: 'Critical', count: stats.alerts_by_severity.critical, color: '#EF4444' },
        { name: 'High', count: stats.alerts_by_severity.high, color: '#F97316' },
        { name: 'Medium', count: stats.alerts_by_severity.medium, color: '#F59E0B' },
        { name: 'Low', count: stats.alerts_by_severity.low, color: '#3B82F6' },
        { name: 'Info', count: stats.alerts_by_severity.info, color: '#6B7280' },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Top action row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">Security Operations Overview</h1>
          <p className="text-xs text-slate-400 mt-0.5">Real-time endpoint telemetry, detections, and incident metrics</p>
        </div>
        <button
          onClick={handleManualRefresh}
          disabled={refreshing}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors w-fit"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Endpoints"
          value={stats?.total_hosts ?? 0}
          subtitle={`${stats?.online_hosts ?? 0} online • ${stats?.offline_hosts ?? 0} offline`}
          icon={<Server className="w-4 h-4 text-emerald-400" />}
          variant={stats && stats.degraded_hosts > 0 ? 'warning' : 'default'}
        />
        <StatsCard
          title="Telemetry Events"
          value={stats?.total_events ?? 0}
          subtitle="Normalized audit events"
          icon={<Activity className="w-4 h-4 text-blue-400" />}
        />
        <StatsCard
          title="Active Alerts"
          value={stats ? stats.new_alerts + stats.investigating_alerts : 0}
          subtitle={`${stats?.new_alerts ?? 0} new • ${stats?.investigating_alerts ?? 0} triage`}
          icon={<AlertOctagon className="w-4 h-4 text-orange-400" />}
          variant={stats && stats.new_alerts > 0 ? 'danger' : 'default'}
        />
        <StatsCard
          title="Open Incidents"
          value={stats?.open_incidents ?? 0}
          subtitle={`${stats?.investigating_incidents ?? 0} actively investigated`}
          icon={<ShieldAlert className="w-4 h-4 text-red-400" />}
          variant={stats && stats.open_incidents > 0 ? 'danger' : 'default'}
        />
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 p-5 rounded-xl border border-slate-800 bg-[#111827]/80">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Telemetry & Detection Activity</h3>
              <p className="text-xs text-slate-400">Hourly events and alert triggers</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-blue-400">
                <span className="w-2.5 h-2.5 rounded bg-blue-500" /> Events
              </span>
              <span className="flex items-center gap-1.5 text-orange-400">
                <span className="w-2.5 h-2.5 rounded bg-orange-500" /> Alerts
              </span>
            </div>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.events_timeline || []}>
                <defs>
                  <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#6B7280" fontSize={11} tickLine={false} />
                <YAxis stroke="#6B7280" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1F2937', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="count" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#colorEvents)" name="Events" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="p-5 rounded-xl border border-slate-800 bg-[#111827]/80 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Alerts by Severity</h3>
            <p className="text-xs text-slate-400 mb-4">Risk level classification breakdown</p>
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityChartData} layout="vertical">
                  <XAxis type="number" stroke="#6B7280" fontSize={11} tickLine={false} />
                  <YAxis type="category" dataKey="name" stroke="#9CA3AF" fontSize={11} tickLine={false} width={60} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1F2937', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {severityChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Total alerts recorded</span>
            <span className="font-semibold text-slate-200">{stats?.total_alerts ?? 0}</span>
          </div>
        </div>
      </div>

      {/* Tables Row: Recent Alerts & Recent Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Recent Detections</h3>
            <button
              onClick={() => onNavigateTab('alerts')}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="divide-y divide-slate-800/60">
            {recentAlerts.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-400">No alerts detected yet</div>
            ) : (
              recentAlerts.map((alt) => (
                <div
                  key={alt.alert_id}
                  onClick={() => onSelectAlert(alt.alert_id)}
                  className="p-3.5 hover:bg-slate-800/40 cursor-pointer transition-colors flex items-center justify-between gap-3 text-xs"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <SeverityBadge severity={alt.severity} size="sm" />
                      <span className="font-semibold text-slate-200 truncate">{alt.title}</span>
                    </div>
                    <p className="text-slate-400 text-[11px] truncate">
                      Host: <span className="text-slate-300 font-mono">{alt.host_id}</span> • Rule: {alt.rule_id}
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <StatusBadge status={alt.status} />
                    <p className="text-[10px] text-slate-400 mt-1 flex items-center justify-end gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(alt.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Events */}
        <div className="rounded-xl border border-slate-800 bg-[#111827]/80 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Live Event Stream</h3>
            <button
              onClick={() => onNavigateTab('events')}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
            >
              <span>Explore</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="divide-y divide-slate-800/60 font-mono text-[11px]">
            {recentEvents.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-400 font-sans">No events ingested yet</div>
            ) : (
              recentEvents.map((ev) => (
                <div key={ev.event_uuid} className="p-3 hover:bg-slate-800/30 flex items-center justify-between gap-3">
                  <div className="truncate">
                    <span className="text-blue-400 font-semibold uppercase">{ev.event_type.replace('_', ' ')}</span>
                    <span className="text-slate-400 mx-2">•</span>
                    <span className="text-slate-200">
                      {ev.process_name || ev.file_path || ev.network_remote_ip || 'telemetry'}
                    </span>
                    {ev.command_line && (
                      <p className="text-slate-400 text-[10px] truncate mt-0.5 max-w-sm">
                        {ev.command_line}
                      </p>
                    )}
                  </div>
                  <span className="text-slate-400 text-[10px] shrink-0">
                    {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
