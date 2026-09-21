import { Navigate, useLocation, Link } from 'react-router-dom';
import useStore from '../../context/store';

/**
 * Protects routes by login + optional allowed roles.
 */
export default function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, currentRole } = useStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (roles?.length && !roles.includes(currentRole)) {
    return (
      <div className="max-w-lg mx-auto px-4 py-16 text-center">
        <h1 className="font-display text-2xl font-bold">Wrong portal</h1>
        <p className="text-slate-600 mt-2 text-sm">
          Your account role is <strong>{currentRole}</strong>. This page is for: {roles.join(', ')}.
        </p>
        <Link to="/dashboard" className="btn-primary mt-6 inline-flex">Go to my workspace</Link>
      </div>
    );
  }

  return children;
}
