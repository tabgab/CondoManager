// @ts-nocheck
import { useState } from 'react';
import api from '../lib/api';
import { useAuthStore } from '../store/auth';
import { Navbar } from '../components/Navbar';
import { ReportList } from '../components/reports/ReportList';
import { TaskList } from '../components/tasks/TaskList';
import { ManagerTaskDetail } from '../components/tasks/ManagerTaskDetail';
import { 
  useUsers, 
  useBuildings, 
  useReports, 
  useTasks,
  useTaskDetail,
  useTaskMessages,
  useReassignTask,
  useUnassignTask,
  useVerifyTask,
  useAddTaskMessage,
} from '../hooks/useQueries';

import type { Task } from '../types';

type Tab = 'overview' | 'reports' | 'tasks' | 'users';

export function ManagerDashboard() {
  const { user, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // Fetch data for stats and modals
  const { data: reportsData } = useReports({ status: 'pending' });
  const { data: tasksData } = useTasks({ status: 'pending' });
  const { data: usersData } = useUsers();
  const { data: selectedTask } = useTaskDetail(selectedTaskId);
  const { data: taskMessages } = useTaskMessages(selectedTaskId);
  
  // Task mutations
  const reassignTask = useReassignTask();
  const unassignTask = useUnassignTask();
  const verifyTask = useVerifyTask();
  const addTaskMessage = useAddTaskMessage();

  const stats = {
    pendingReports: reportsData?.total || 0,
    activeTasks: tasksData?.total || 0,
    totalUsers: usersData?.total || 0,
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTaskId(task.id);
  };

  const handleCloseDetail = () => {
    setSelectedTaskId(null);
  };

  const handleAssign = async (employeeId: string) => {
    if (selectedTaskId) {
      await reassignTask.mutateAsync({ taskId: selectedTaskId, assigneeId: employeeId });
    }
  };

  const handleUnassign = async () => {
    if (selectedTaskId) {
      await unassignTask.mutateAsync({ taskId: selectedTaskId });
    }
  };

  const handleVerify = async () => {
    if (selectedTaskId) {
      await verifyTask.mutateAsync({ taskId: selectedTaskId });
    }
  };

  const handleSendMessage = async (content: string) => {
    if (selectedTaskId) {
      await addTaskMessage.mutateAsync({ taskId: selectedTaskId, content });
    }
  };

  const employees = usersData?.items.filter(u => u.role === 'employee') || [];

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'reports', label: 'Reports' },
    { id: 'tasks', label: 'Tasks' },
    { id: 'users', label: 'Users' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={logout} />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">
            Manager Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Welcome, {user?.first_name || user?.email}!
          </p>

          {/* Tabs */}
          <div className="mt-8 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                    ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {/* Stats Cards */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Pending Reports</dt>
                          <dd className="text-lg font-medium text-gray-900">{stats.pendingReports}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-5 py-3">
                    <button
                      onClick={() => setActiveTab('reports')}
                      className="text-sm font-medium text-blue-600 hover:text-blue-500"
                    >
                      View reports
                    </button>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Active Tasks</dt>
                          <dd className="text-lg font-medium text-gray-900">{stats.activeTasks}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-5 py-3">
                    <button
                      onClick={() => setActiveTab('tasks')}
                      className="text-sm font-medium text-blue-600 hover:text-blue-500"
                    >
                      View tasks
                    </button>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                          <dd className="text-lg font-medium text-gray-900">{stats.totalUsers}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'tasks' && (
              <>
                <TaskList 
                  onTaskClick={handleTaskClick}
                  onCreateTask={() => setShowCreateTask(true)} 
                />
                <ManagerTaskDetail
                  task={selectedTask || null}
                  isOpen={!!selectedTaskId}
                  onClose={handleCloseDetail}
                  employees={employees}
                  messages={taskMessages || []}
                  onAssign={handleAssign}
                  onUnassign={handleUnassign}
                  onVerify={handleVerify}
                  onSendMessage={handleSendMessage}
                  isAssigning={reassignTask.isPending}
                  isVerifying={verifyTask.isPending}
                />
              </>
            )}

            {activeTab === 'reports' && (
              <ReportList />
            )}

            {activeTab === 'users' && (
              <UsersTabWithAdd />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// Users Tab Component
// Users Tab with Add User functionality
function UsersTabWithAdd() {
  const { data, isLoading, error, refetch } = useUsers();
  const users = data?.items || [];
  const [showAddUser, setShowAddUser] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    role: 'employee' as string,
    phone: '',
  });

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdding(true);
    setAddError(null);
    try {
      await api.post('/auth/register', form);
      setShowAddUser(false);
      setForm({ first_name: '', last_name: '', email: '', password: '', role: 'employee', phone: '' });
      refetch();
    } catch (err: any) {
      setAddError(err?.response?.data?.detail || 'Failed to add user');
    } finally {
      setAdding(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <h3 className="text-sm font-medium text-red-800">Error loading users</h3>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Users ({users.length})</h3>
        <button
          onClick={() => setShowAddUser(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          + Add User
        </button>
      </div>

      {showAddUser && (
        <div className="mb-6 bg-white shadow rounded-lg p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Add New User</h4>
          {addError && (
            <div className="mb-4 rounded-md bg-red-50 p-3">
              <p className="text-sm text-red-700">{addError}</p>
            </div>
          )}
          <form onSubmit={handleAdd} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">First Name</label>
              <input type="text" required value={form.first_name}
                onChange={e => setForm({...form, first_name: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Last Name</label>
              <input type="text" required value={form.last_name}
                onChange={e => setForm({...form, last_name: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input type="email" required value={form.email}
                onChange={e => setForm({...form, email: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <input type="password" required minLength={8} value={form.password}
                onChange={e => setForm({...form, password: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Role</label>
              <select value={form.role} onChange={e => setForm({...form, role: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                <option value="employee">Employee</option>
                <option value="owner">Owner</option>
                <option value="tenant">Tenant</option>
                <option value="manager">Manager</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Phone (optional)</label>
              <input type="tel" value={form.phone}
                onChange={e => setForm({...form, phone: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              />
            </div>
            <div className="sm:col-span-2 flex justify-end space-x-3">
              <button type="button" onClick={() => setShowAddUser(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button type="submit" disabled={adding}
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {adding ? 'Adding...' : 'Add User'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {users.length === 0 ? (
            <li className="px-6 py-8 text-center text-gray-500">No users found. Add one above.</li>
          ) : (
            users.map((user) => (
              <li key={user.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                    {user.phone && <p className="text-xs text-gray-400">{user.phone}</p>}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                      user.role === 'manager' ? 'bg-purple-100 text-purple-800' :
                      user.role === 'employee' ? 'bg-green-100 text-green-800' :
                      user.role === 'owner' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.role}
                    </span>
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${
                      user.is_active ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}

export default ManagerDashboard;
