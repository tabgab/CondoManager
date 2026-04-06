import { useState } from 'react';
import { useAuthStore } from '../store/auth';
import { Navbar } from '../components/Navbar';
import { WeeklyTaskView } from '../components/tasks/WeeklyTaskView';
import { TaskDetail } from '../components/tasks/TaskDetail';
import { TaskUpdateForm } from '../components/tasks/TaskUpdateForm';
import { useMyAssignedTasks, useUpdateTaskStatus, useAddTaskUpdate } from '../hooks/useQueries';
import type { Task, TaskUpdate } from '../types';

export function EmployeeDashboard() {
  const { user, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'calendar' | 'today'>('calendar');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showTaskDetail, setShowTaskDetail] = useState(false);
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [currentWeekOffset, setCurrentWeekOffset] = useState(0);

  const { data: tasksResponse, isLoading: tasksLoading, refetch } = useMyAssignedTasks();
  const tasks = tasksResponse?.items || [];
  
  const updateStatus = useUpdateTaskStatus();
  const addUpdate = useAddTaskUpdate();

  const today = new Date();
  const currentWeekStart = new Date(today);
  currentWeekStart.setDate(today.getDate() + (currentWeekOffset * 7));

  const assignedCount = tasks.length;
  const inProgressCount = tasks.filter(t => t.status === 'in_progress').length;
  const todayCompleted = tasks.filter(t => 
    t.status === 'completed' && 
    t.updated_at && 
    new Date(t.updated_at).toDateString() === new Date().toDateString()
  ).length;

  const todaysTasks = tasks.filter(t => {
    if (!t.due_date) return false;
    const due = new Date(t.due_date);
    return due.toDateString() === new Date().toDateString();
  });

  const handleTaskClick = (taskId: string) => {
    const task = tasks.find(t => t.id === taskId);
    if (task) {
      setSelectedTask(task);
      setShowTaskDetail(true);
      setShowUpdateForm(false);
    }
  };

  const handleCloseDetail = () => {
    setShowTaskDetail(false);
    setSelectedTask(null);
    setShowUpdateForm(false);
  };

  const handleMarkComplete = async () => {
    if (!selectedTask) return;
    
    try {
      await updateStatus.mutateAsync({ 
        taskId: selectedTask.id, 
        status: 'completed' 
      });
      refetch();
      handleCloseDetail();
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const handleAddUpdate = () => {
    setShowUpdateForm(true);
  };

  const handleSubmitUpdate = async (content: string, isConcern: boolean) => {
    if (!selectedTask) return;
    
    try {
      await addUpdate.mutateAsync({
        taskId: selectedTask.id,
        content,
        isConcern,
      });
      setShowUpdateForm(false);
      refetch();
    } catch (error) {
      console.error('Failed to add update:', error);
    }
  };

  const getMockUpdates = (task: Task): TaskUpdate[] => {
    // In a real app, these would come from a separate query
    return [];
  };

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

          {/* Stats Cards */}
          <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Assigned Tasks</dt>
                      <dd className="text-3xl font-semibold text-gray-900">{assignedCount}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">In Progress</dt>
                      <dd className="text-3xl font-semibold text-gray-900">{inProgressCount}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Completed Today</dt>
                      <dd className="text-3xl font-semibold text-gray-900">{todayCompleted}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-8">
            <div className="sm:hidden">
              <label htmlFor="tabs" className="sr-only">Select a tab</label>
              <select
                id="tabs"
                name="tabs"
                className="block w-full focus:ring-blue-500 focus:border-blue-500 border-gray-300 rounded-md"
                value={activeTab}
                onChange={(e) => setActiveTab(e.target.value as 'calendar' | 'today')}
              >
                <option value="calendar">Weekly Calendar</option>
                <option value="today">Today/Upcoming</option>
              </select>
            </div>
            <div className="hidden sm:block">
              <nav className="flex space-x-4" aria-label="Tabs">
                <button
                  onClick={() => setActiveTab('calendar')}
                  className={`${
                    activeTab === 'calendar'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  } px-3 py-2 font-medium text-sm rounded-md`}
                >
                  Weekly Calendar
                </button>
                <button
                  onClick={() => setActiveTab('today')}
                  className={`${
                    activeTab === 'today'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  } px-3 py-2 font-medium text-sm rounded-md`}
                >
                  Today/Upcoming
                </button>
              </nav>
            </div>
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {tasksLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
              </div>
            ) : (
              <>
                {activeTab === 'calendar' && (
                  <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
                    {/* Week Navigation */}
                    <div className="flex items-center justify-between mb-4">
                      <button
                        onClick={() => setCurrentWeekOffset(currentWeekOffset - 1)}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        ← Previous Week
                      </button>
                      <button
                        onClick={() => setCurrentWeekOffset(0)}
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        Current Week
                      </button>
                      <button
                        onClick={() => setCurrentWeekOffset(currentWeekOffset + 1)}
                        className="text-gray-600 hover:text-gray-900"
                      >
                        Next Week →
                      </button>
                    </div>
                    <WeeklyTaskView
                      tasks={tasks}
                      onTaskClick={handleTaskClick}
                      currentDate={currentWeekStart}
                    />
                  </div>
                )}

                {activeTab === 'today' && (
                  <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div className="px-4 py-5 sm:px-6">
                      <h3 className="text-lg leading-6 font-medium text-gray-900">
                        Today's Tasks
                      </h3>
                      <p className="mt-1 max-w-2xl text-sm text-gray-500">
                        Tasks due today
                      </p>
                    </div>
                    <div className="border-t border-gray-200">
                      {todaysTasks.length === 0 ? (
                        <div className="px-4 py-8 text-center text-gray-500">
                          <p>No tasks due today.</p>
                        </div>
                      ) : (
                        <ul className="divide-y divide-gray-200">
                          {todaysTasks.map((task) => (
                            <li key={task.id} className="px-4 py-4">
                              <button
                                onClick={() => handleTaskClick(task.id)}
                                className="w-full text-left flex items-center justify-between hover:bg-gray-50 -mx-4 px-4 py-2"
                              >
                                <div>
                                  <p className="text-sm font-medium text-gray-900">{task.title}</p>
                                  <p className="text-sm text-gray-500">{task.building?.name || 'No building'}</p>
                                </div>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  task.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                  task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                  task.status === 'completed' ? 'bg-green-100 text-green-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {task.status.replace('_', ' ')}
                                </span>
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>

      {/* Task Detail Modal */}
      {showTaskDetail && selectedTask && !showUpdateForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={handleCloseDetail} />
            <div className="relative z-10">
              <TaskDetail
                task={selectedTask}
                updates={getMockUpdates(selectedTask)}
                onClose={handleCloseDetail}
                onComplete={handleMarkComplete}
                onAddUpdate={handleAddUpdate}
                isLoading={updateStatus.isPending}
              />
            </div>
          </div>
        </div>
      )}

      {/* Task Update Form Modal */}
      {showUpdateForm && selectedTask && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={() => setShowUpdateForm(false)} />
            <div className="relative z-10 bg-white rounded-lg shadow-lg max-w-lg w-full p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Add Update for: {selectedTask.title}
              </h3>
              <TaskUpdateForm
                taskId={selectedTask.id}
                onSubmit={handleSubmitUpdate}
                onCancel={() => setShowUpdateForm(false)}
                isLoading={addUpdate.isPending}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default EmployeeDashboard;
