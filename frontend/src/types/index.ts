/**
 * TypeScript Type Definitions for SentinelEDR Frontend
 */

export interface AnalystUser {
  id: number;
  username: string;
  role: 'admin' | 'analyst' | 'viewer';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AnalystUser;
}

export interface Host {
  id: number;
  host_id: string;
  hostname: string;
  os_platform: string;
  os_version?: string;
  agent_version: string;
  first_seen: string;
  last_seen: string;
  status: 'online' | 'offline' | 'degraded' | 'stale';
  ip_addresses: string[];
  system_info: Record<string, any>;
  is_synthetic: boolean;
  alerts_count: number;
}

export interface SecurityEvent {
  id: number;
  event_uuid: string;
  host_id: string;
  event_type: 'process_creation' | 'network_connection' | 'file_activity' | 'agent_health';
  timestamp: string;
  ingested_at: string;
  schema_version: string;
  data: Record<string, any>;
  process_name?: string;
  process_id?: number;
  parent_process_name?: string;
  parent_process_id?: number;
  command_line?: string;
  username?: string;
  network_remote_ip?: string;
  network_remote_port?: number;
  network_protocol?: string;
  file_path?: string;
  file_action?: string;
  is_synthetic: boolean;
}

export interface DetectionRule {
  id: number;
  rule_id: string;
  name: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: string;
  enabled: boolean;
  conditions: Record<string, any>;
  mitre_technique_id?: string;
  mitre_technique_name?: string;
  mitre_tactic?: string;
  version: string;
  rationale?: string;
  evidence_fields: string[];
  false_positive_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: number;
  alert_id: string;
  rule_id: string;
  host_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'new' | 'acknowledged' | 'investigating' | 'resolved' | 'false_positive';
  title: string;
  description: string;
  evidence_summary: Record<string, any>;
  mitre_technique_id?: string;
  mitre_technique_name?: string;
  mitre_tactic?: string;
  first_seen: string;
  last_seen: string;
  event_count: number;
  assigned_to?: string;
  incident_id?: string;
  false_positive_reason?: string;
  created_at: string;
  updated_at: string;
  is_synthetic: boolean;
  events?: SecurityEvent[];
}

export interface InvestigationNote {
  id: string;
  author: string;
  text: string;
  timestamp: string;
}

export interface Incident {
  id: number;
  incident_id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'investigating' | 'contained' | 'resolved' | 'closed';
  assigned_to?: string;
  investigation_notes: InvestigationNote[];
  created_at: string;
  updated_at: string;
  is_synthetic: boolean;
  alerts?: Alert[];
}

export interface AuditLog {
  id: number;
  actor_username: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details: Record<string, any>;
  timestamp: string;
  ip_address?: string;
}

export interface DashboardStats {
  total_hosts: number;
  online_hosts: number;
  offline_hosts: number;
  degraded_hosts: number;
  total_events: number;
  total_alerts: number;
  new_alerts: number;
  investigating_alerts: number;
  resolved_alerts: number;
  alerts_by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  total_incidents: number;
  open_incidents: number;
  investigating_incidents: number;
  demo_mode: boolean;
  events_timeline: Array<{ time: string; count: number }>;
  alerts_timeline: Array<{ time: string; count: number }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
