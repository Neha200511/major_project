import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SocketProvider } from './context/SocketContext';
import { AppLayout } from './layouts/AppLayout';
import { LoadingSpinner } from './components/common/States';

// Pages
import { LandingPage } from './pages/LandingPage';
import { RoleSelectionPage } from './pages/RoleSelectionPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfilePage } from './pages/ProfilePage';
import { DevPanel } from './pages/DevPanel';

// Child Pages
import { ChildDashboard } from './pages/child/ChildDashboard';
import { ChildChat } from './pages/child/ChildChat';
import { ContactsPage } from './pages/child/ContactsPage';
import { SafetyStatus } from './pages/child/SafetyStatus';

// Contact Pages
import { ContactDashboard } from './pages/contact/ContactDashboard';
import { ContactChat } from './pages/contact/ContactChat';

// Parent Pages
import { ParentDashboard } from './pages/parent/ParentDashboard';
import { ParentConversations } from './pages/parent/ParentConversations';
import { ParentAlerts } from './pages/parent/ParentAlerts';
import { ConversationRisk } from './pages/parent/ConversationRisk';
import { BehaviourTrends } from './pages/parent/BehaviourTrends';
import { Reports } from './pages/parent/Reports';
import { ParentSettings } from './pages/parent/ParentSettings';

// Role-protected route wrapper
const ProtectedRoute: React.FC<{
  allowedRoles?: string[];
  children: React.ReactNode;
}> = ({ allowedRoles, children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <LoadingSpinner size="lg" text="Authenticating secure session..." />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to their respective home
    if (user.role === 'CHILD') return <Navigate to="/child" replace />;
    if (user.role === 'PARENT') return <Navigate to="/parent" replace />;
    return <Navigate to="/contact" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <SocketProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/select-role" element={<RoleSelectionPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Authenticated Layout Routes */}
            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              {/* Child Routes */}
              <Route
                path="/child"
                element={
                  <ProtectedRoute allowedRoles={['CHILD']}>
                    <ChildDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/child/chat/:conversationId"
                element={
                  <ProtectedRoute allowedRoles={['CHILD']}>
                    <ChildChat />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/child/contacts"
                element={
                  <ProtectedRoute allowedRoles={['CHILD']}>
                    <ContactsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/child/safety"
                element={
                  <ProtectedRoute allowedRoles={['CHILD']}>
                    <SafetyStatus />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/child/profile"
                element={
                  <ProtectedRoute allowedRoles={['CHILD']}>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* Contact Routes */}
              <Route
                path="/contact"
                element={
                  <ProtectedRoute allowedRoles={['CONTACT']}>
                    <ContactDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/contact/chat/:conversationId"
                element={
                  <ProtectedRoute allowedRoles={['CONTACT']}>
                    <ContactChat />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/contact/profile"
                element={
                  <ProtectedRoute allowedRoles={['CONTACT']}>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* Parent Routes */}
              <Route
                path="/parent"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <ParentDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parent/conversations"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <ParentConversations />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parent/alerts"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <ParentAlerts />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parent/risk/:conversationId"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <ConversationRisk />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parent/trends"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <BehaviourTrends />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parent/reports"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <Reports />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parent/settings"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <ParentSettings />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parent/profile"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* Development Panel (Admin/Demo) */}
              <Route
                path="/dev"
                element={
                  <ProtectedRoute allowedRoles={['PARENT']}>
                    <DevPanel />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </SocketProvider>
    </AuthProvider>
  );
};

export default App;
