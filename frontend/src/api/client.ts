/**
 * API Client for SentinelEDR Backend
 */

import {
  TokenResponse,
  AnalystUser,
  Host,
  SecurityEvent,
  DetectionRule,
  Alert,
  Incident,
  AuditLog,
  DashboardStats,
  PaginatedResponse
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

class ApiClient {
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    const token = localStorage.getItem('sentinel_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (response.status === 401) {
      localStorage.removeItem('sentinel_token');
      localStorage.removeItem('sentinel_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      throw new Error('Session expired or unauthorized');
    }

    if (!response.ok) {
      let errorMsg = `HTTP Error ${response.status}`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorMsg = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // Fallback to status text
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  // Auth
  async login(username: string, password: string): Promise<TokenResponse> {
    return this.request<TokenResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async getMe(): Promise<AnalystUser> {
    return this.request<AnalystUser>('/api/v1/auth/me');
  }

  // Stats
  async getStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>('/api/v1/stats');
  }

  // Hosts
  async getHosts(params?: { status?: string; search?: string; page?: number; page_size?: number }): Promise<PaginatedResponse<Host>> {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.search) query.set('search', params.search);
    if (params?.page) query.set('page', params.page.toString());
    if (params?.page_size) query.set('page_size', params.page_size.toString());
    return this.request<PaginatedResponse<Host>>(`/api/v1/hosts?${query.toString()}`);
  }

  async getHost(hostId: string): Promise<Host> {
    return this.request<Host>(`/api/v1/hosts/${hostId}`);
  }

  // Events
  async getEvents(params?: {
    host_id?: string;
    event_type?: string;
    process_name?: string;
    search?: string;
    is_synthetic?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<SecurityEvent>> {
    const query = new URLSearchParams();
    if (params?.host_id) query.set('host_id', params.host_id);
    if (params?.event_type) query.set('event_type', params.event_type);
    if (params?.process_name) query.set('process_name', params.process_name);
    if (params?.search) query.set('search', params.search);
    if (params?.is_synthetic !== undefined) query.set('is_synthetic', params.is_synthetic.toString());
    if (params?.page) query.set('page', params.page.toString());
    if (params?.page_size) query.set('page_size', params.page_size.toString());
    return this.request<PaginatedResponse<SecurityEvent>>(`/api/v1/events?${query.toString()}`);
  }

  async getEvent(eventId: string): Promise<SecurityEvent> {
    return this.request<SecurityEvent>(`/api/v1/events/${eventId}`);
  }

  // Alerts
  async getAlerts(params?: {
    severity?: string;
    status?: string;
    host_id?: string;
    rule_id?: string;
    search?: string;
    is_synthetic?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Alert>> {
    const query = new URLSearchParams();
    if (params?.severity) query.set('severity', params.severity);
    if (params?.status) query.set('status', params.status);
    if (params?.host_id) query.set('host_id', params.host_id);
    if (params?.rule_id) query.set('rule_id', params.rule_id);
    if (params?.search) query.set('search', params.search);
    if (params?.is_synthetic !== undefined) query.set('is_synthetic', params.is_synthetic.toString());
    if (params?.page) query.set('page', params.page.toString());
    if (params?.page_size) query.set('page_size', params.page_size.toString());
    return this.request<PaginatedResponse<Alert>>(`/api/v1/alerts?${query.toString()}`);
  }

  async getAlert(alertId: string): Promise<Alert> {
    return this.request<Alert>(`/api/v1/alerts/${alertId}`);
  }

  async updateAlert(alertId: string, data: { status?: string; assigned_to?: string; incident_id?: string; false_positive_reason?: string }): Promise<Alert> {
    return this.request<Alert>(`/api/v1/alerts/${alertId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Incidents
  async getIncidents(params?: {
    status?: string;
    severity?: string;
    assigned_to?: string;
    search?: string;
    is_synthetic?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Incident>> {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.severity) query.set('severity', params.severity);
    if (params?.assigned_to) query.set('assigned_to', params.assigned_to);
    if (params?.search) query.set('search', params.search);
    if (params?.is_synthetic !== undefined) query.set('is_synthetic', params.is_synthetic.toString());
    if (params?.page) query.set('page', params.page.toString());
    if (params?.page_size) query.set('page_size', params.page_size.toString());
    return this.request<PaginatedResponse<Incident>>(`/api/v1/incidents?${query.toString()}`);
  }

  async getIncident(incidentId: string): Promise<Incident> {
    return this.request<Incident>(`/api/v1/incidents/${incidentId}`);
  }

  async createIncident(data: { title: string; description: string; severity?: string; assigned_to?: string; alert_ids?: string[] }): Promise<Incident> {
    return this.request<Incident>('/api/v1/incidents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateIncident(incidentId: string, data: {
    title?: string;
    description?: string;
    severity?: string;
    status?: string;
    assigned_to?: string;
    add_note?: string;
    link_alert_ids?: string[];
    unlink_alert_ids?: string[];
  }): Promise<Incident> {
    return this.request<Incident>(`/api/v1/incidents/${incidentId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Rules
  async getRules(params?: { severity?: string; category?: string; enabled?: boolean }): Promise<DetectionRule[]> {
    const query = new URLSearchParams();
    if (params?.severity) query.set('severity', params.severity);
    if (params?.category) query.set('category', params.category);
    if (params?.enabled !== undefined) query.set('enabled', params.enabled.toString());
    return this.request<DetectionRule[]>(`/api/v1/rules?${query.toString()}`);
  }

  async getRule(ruleId: string): Promise<DetectionRule> {
    return this.request<DetectionRule>(`/api/v1/rules/${ruleId}`);
  }

  async toggleRule(ruleId: string, enabled: boolean): Promise<DetectionRule> {
    return this.request<DetectionRule>(`/api/v1/rules/${ruleId}/toggle`, {
      method: 'PATCH',
      body: JSON.stringify({ enabled }),
    });
  }

  // Audit Logs
  async getAuditLogs(params?: { actor?: string; action?: string; resource_type?: string; page?: number; page_size?: number }): Promise<PaginatedResponse<AuditLog>> {
    const query = new URLSearchParams();
    if (params?.actor) query.set('actor', params.actor);
    if (params?.action) query.set('action', params.action);
    if (params?.resource_type) query.set('resource_type', params.resource_type);
    if (params?.page) query.set('page', params.page.toString());
    if (params?.page_size) query.set('page_size', params.page_size.toString());
    return this.request<PaginatedResponse<AuditLog>>(`/api/v1/audit-logs?${query.toString()}`);
  }
}

export const api = new ApiClient();
