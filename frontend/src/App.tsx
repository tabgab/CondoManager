import { Routes, Route, Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from './store/auth';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Login } from './pages/Login';
import { Unauthorized } from './pages/Unauthorized';
import { ManagerDashboard } from './pages/ManagerDashboard';
import { EmployeeDashboard } from './pages/EmployeeDashboard';
import { OwnerDashboard } from './pages/OwnerDashboard';
import './index.css';

// Component to handle root redirect based on auth
function RootRedirect() {
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  const role = user.role;
  if (role === 'manager' || role === 'super_admin') {
    return <Navigate to="/manager/dashboard" replace />;
  } else if (role === 'employee') {
    return <Navigate to="/employee/dashboard" replace />;
  } else if (role === 'owner' || role === 'tenant') {
    return <Navigate to="/owner/dashboard" replace />;
  }
  return <Navigate to="/login" replace />;
}

// Main app routes wrapper
function AppRoutes() {
  return (
    <div data-testid="app-container">
      <Routes>
        {/* Root - redirect based on auth status and role */}
        <Route path="/" element={<RootRedirect />} />

        {/* Login - accessible to all */}
        <Route path="/login" element={<Login />} />

        {/* Unauthorized */}
        <Route path="/unauthorized" element={<Unauthorized />} />

        {/* Manager Dashboard - protected, manager only */}
        <Route
          path="/manager/dashboard"
          element={
            <ProtectedRoute requiredRoles={['manager', 'super_admin']}>
              <ManagerDashboard />
            </ProtectedRoute>
          }
        />

        {/* Employee Dashboard - protected, employee only */}
        <Route
          path="/employee/dashboard"
          element={
            <ProtectedRoute requiredRoles={['employee']}>
              <EmployeeDashboard />
            </ProtectedRoute>
          }
        />

        {/* Owner/Tenant Dashboard - protected */}
        <Route
          path="/owner/dashboard"
          element={
            <ProtectedRoute requiredRoles={['owner', 'tenant']}>
              <OwnerDashboard />
            </ProtectedRoute>
          }
        />

        {/* Catch all - redirect to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  );
}

function App() {
  return <AppRoutes />;
}

export default App;
