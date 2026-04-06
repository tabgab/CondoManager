import { useAuthStore } from '../store/auth';
import { Navbar } from '../components/Navbar';

export function EmployeeDashboard() {
  const { user, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={logout} />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">
            Employee Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Welcome, {user?.first_name || user?.email}!
          </p>
          
          <div className="mt-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">My Tasks</h2>
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <div className="p-8 text-center text-gray-500">
                <p>No tasks assigned yet.</p>
                <p className="text-sm mt-2">Check back later for new assignments.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default EmployeeDashboard;
