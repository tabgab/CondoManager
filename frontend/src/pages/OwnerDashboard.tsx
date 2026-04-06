import { useAuthStore } from '../store/auth';
import { Navbar } from '../components/Navbar';

export function OwnerDashboard() {
  const { user, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={logout} />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">
            Owner Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Welcome, {user?.first_name || user?.email}!
          </p>
          
          <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  My Reports
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                  Track the status of your reported issues.
                </p>
              </div>
              <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                <div className="py-8 text-center text-gray-500">
                  <p>No reports submitted yet.</p>
                  <button className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Submit a new report
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  My Apartment
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                  View your apartment details.
                </p>
              </div>
              <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                <div className="py-8 text-center text-gray-500">
                  <p>Apartment information will appear here.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default OwnerDashboard;
