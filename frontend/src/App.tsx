import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DemoBanner } from './components/DemoBanner';
import { Login } from './pages/Login';
import { Overview } from './pages/Overview';
import { Endpoints } from './pages/Endpoints';
import { EventExplorer } from './pages/EventExplorer';
import { Alerts } from './pages/Alerts';
import { AlertDetails } from './pages/AlertDetails';
import { Incidents } from './pages/Incidents';
import { IncidentDetails } from './pages/IncidentDetails';
import { Rules } from './pages/Rules';
import { AuditLogs } from './pages/AuditLogs';
import { Settings } from './pages/Settings';
import { api } from './api/client';

const DashboardLayout: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      api.getStats()
        .then((s) => setDemoMode(s.demo_mode))
        .catch(() => {});
    }
  }, [isAuthenticated, currentTab]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0F19] flex items-center justify-center text-slate-400 text-sm">
        <div className="animate-pulse">Loading SentinelEDR Console...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  const handleSelectAlert = (alertId: string) => {
    setSelectedAlertId(alertId);
    setCurrentTab('alert-details');
  };

  const handleSelectIncident = (incidentId: string) => {
    setSelectedIncidentId(incidentId);
    setCurrentTab('incident-details');
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Persistent Demo Mode Banner */}
      <DemoBanner show={demoMode} />

      {/* Main Top Navigation */}
      <Navbar demoMode={demoMode} />

      {/* Body with Sidebar and Active Workspace */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentTab={currentTab.includes('details') ? currentTab.split('-')[0] + 's' : currentTab}
          onTabChange={(tab) => {
            setCurrentTab(tab);
            setSelectedAlertId(null);
            setSelectedIncidentId(null);
          }}
        />

        <main className="flex-1 p-6 overflow-y-auto bg-[#0B0F19]">
          <div className="max-w-7xl mx-auto">
            {currentTab === 'overview' && (
              <Overview onSelectAlert={handleSelectAlert} onNavigateTab={setCurrentTab} />
            )}

            {currentTab === 'endpoints' && <Endpoints />}

            {currentTab === 'events' && <EventExplorer />}

            {currentTab === 'alerts' && <Alerts onSelectAlert={handleSelectAlert} />}

            {currentTab === 'alert-details' && selectedAlertId && (
              <AlertDetails
                alertId={selectedAlertId}
                onBack={() => setCurrentTab('alerts')}
                onNavigateToIncident={handleSelectIncident}
              />
            )}

            {currentTab === 'incidents' && (
              <Incidents onSelectIncident={handleSelectIncident} />
            )}

            {currentTab === 'incident-details' && selectedIncidentId && (
              <IncidentDetails
                incidentId={selectedIncidentId}
                onBack={() => setCurrentTab('incidents')}
                onSelectAlert={handleSelectAlert}
              />
            )}

            {currentTab === 'rules' && <Rules />}

            {currentTab === 'audit' && <AuditLogs />}

            {currentTab === 'settings' && <Settings />}
          </div>
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <DashboardLayout />
    </AuthProvider>
  );
}

export default App;
