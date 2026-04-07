import { ReactNode, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/auth';
import type { UserRole } from '../types/auth';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRoles?: UserRole[];
}

export function ProtectedRoute({ children, requiredRoles }: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading, _hasHydrated, checkAuth } = useAuthStore();
  const location = useLocation();

  // Check auth on mount if we have a token but no user
  useEffect(() => {
    if (_hasHydrated && isAuthenticated && !user) {
      checkAuth();
    }
  }, [_hasHydrated, isAuthenticated, user, checkAuth]);

  // Wait for Zustand to rehydrate from localStorage before making auth decisions
  // This prevents the flash-redirect caused by initial isAuthenticated=false
  if (!_hasHydrated || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role authorization
  if (requiredRoles && user) {
    const hasRequiredRole = requiredRoles.includes(user.role);
    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // Authorized, render children
  return <>{children}</>;
}

export default ProtectedRoute;
