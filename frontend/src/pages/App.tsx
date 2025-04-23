import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import WorkflowBuilderWrapper from '../components/WorkflowBuilder/WorkflowBuilderWrapper';
import { NodeTypesProvider } from '../contexts/NodeTypesContext';
import { NodeDiscoveryProvider } from '../contexts/NodeDiscoveryContext';
import { AuthProvider } from '../contexts/AuthContext';
import { WebSocketProvider } from '../contexts/WebSocketContext';
import { ThemeProvider } from '../contexts/ThemeContext';
import { NodeConfigProvider } from '../contexts/NodeConfigContext';
import { DemoModeProvider } from '../contexts/DemoModeContext';
import LoginForm from '../components/Auth/LoginForm';
import RegisterForm from '../components/Auth/RegisterForm';
import UserProfile from '../components/Auth/UserProfile';
import ProtectedRoute from '../components/Auth/ProtectedRoute';
import ScheduleList from '../components/Schedules/ScheduleList';
import ScheduleForm from '../components/Schedules/ScheduleForm';
import ScheduleDetails from '../components/Schedules/ScheduleDetails';
import ExecutionResults from '../components/Workflow/ExecutionResults';
import Layout from '../components/Layout/Layout';
import Dashboard from '../components/Dashboard/Dashboard';
import NotFound from '../components/Layout/NotFound';
import Unauthorized from '../components/Layout/Unauthorized';

const App: React.FC = () => {
  // Use keys to force the providers to re-render
  const discoveryKey = 'node-discovery-provider-' + Date.now();
  const typesKey = 'node-types-provider-' + Date.now();

  // Force a re-render of the providers
  React.useEffect(() => {
    console.log('App mounted, forcing provider initialization');

    // Clear any cached data in localStorage
    try {
      localStorage.removeItem('nodeDiscoveryContext');
      localStorage.removeItem('nodeTypesContext');
    } catch (e) {
      console.warn('Failed to clear localStorage:', e);
    }
  }, []);

  return (
    <div className="App">
      <Router>
        <ThemeProvider>
          <DemoModeProvider>
            <AuthProvider>
              <WebSocketProvider>
                <NodeDiscoveryProvider key={discoveryKey}>
                  <NodeTypesProvider key={typesKey}>
                    <NodeConfigProvider>
                    <Routes>
                      {/* Public routes */}
                      <Route path="/login" element={<LoginForm />} />
                      <Route path="/register" element={<RegisterForm />} />
                      <Route path="/unauthorized" element={<Unauthorized />} />

                      {/* Protected routes */}
                      <Route path="/" element={
                        <ProtectedRoute>
                          <Layout />
                        </ProtectedRoute>
                      }>
                        <Route index element={<Dashboard />} />
                        <Route path="profile" element={<UserProfile />} />

                        {/* Workflow routes */}
                        <Route path="workflows" element={<WorkflowBuilderWrapper />} />
                        <Route path="workflows/:workflowId" element={<WorkflowBuilderWrapper />} />
                        <Route path="workflows/execution/:executionId" element={<ExecutionResults />} />

                        {/* Schedule routes */}
                        <Route path="schedules" element={<ScheduleList />} />
                        <Route path="schedules/new" element={<ScheduleForm />} />
                        <Route path="schedules/:scheduleId" element={<ScheduleDetails />} />
                        <Route path="schedules/:scheduleId/edit" element={<ScheduleForm />} />
                        <Route path="workflows/:workflowId/schedules" element={<ScheduleList />} />
                        <Route path="workflows/:workflowId/schedules/new" element={<ScheduleForm />} />
                      </Route>

                      {/* Fallback routes */}
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                    </NodeConfigProvider>
                  </NodeTypesProvider>
                </NodeDiscoveryProvider>
              </WebSocketProvider>
            </AuthProvider>
          </DemoModeProvider>
        </ThemeProvider>
      </Router>
    </div>
  );
};

export default App;
