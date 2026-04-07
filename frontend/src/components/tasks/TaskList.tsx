import { useState } from 'react';
import { useTasks } from '../../hooks/useQueries';
import { TaskCard } from './TaskCard';
import type { Task, TaskStatus, TaskPriority } from '../../types';

const statusOptions: { value: TaskStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'completed', label: 'Completed' },
  { value: 'verified', label: 'Verified' },
  { value: 'cancelled', label: 'Cancelled' },
];

const priorityOptions: { value: TaskPriority | ''; label: string }[] = [
  { value: '', label: 'All Priorities' },
  { value: 'low', label: 'Low' },
  { value: 'normal', label: 'Normal' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' },
];

interface TaskListProps {
  onCreateTask?: () => void;
  onTaskClick?: (task: Task) => void;
}

export function TaskList({ onCreateTask, onTaskClick }: TaskListProps) {
  const [selectedStatus, setSelectedStatus] = useState<TaskStatus | ''>('');
  const [selectedPriority, setSelectedPriority] = useState<TaskPriority | ''>('');

  const filters = {
    ...(selectedStatus && { status: selectedStatus }),
    ...(selectedPriority && { priority: selectedPriority }),
  };

  const { data, isLoading, error } = useTasks(
    selectedStatus || selectedPriority ? filters : undefined
  );

  const tasks = data?.items || [];

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
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading tasks</h3>
            <div className="mt-2 text-sm text-red-700">
              {error instanceof Error ? error.message : 'Unknown error'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with Filters and Create Button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 rounded-lg shadow">
        <div className="flex flex-col sm:flex-row gap-4 flex-1">
          <div className="flex-1">
            <label htmlFor="task-status-filter" className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              id="task-status-filter"
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value as TaskStatus | '')}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1">
            <label htmlFor="task-priority-filter" className="block text-sm font-medium text-gray-700">
              Priority
            </label>
            <select
              id="task-priority-filter"
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value as TaskPriority | '')}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              {priorityOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-end gap-2">
          <button
            onClick={() => {
              setSelectedStatus('');
              setSelectedPriority('');
            }}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Clear
          </button>
          {onCreateTask && (
            <button
              onClick={onCreateTask}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <svg className="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Task
            </button>
          )}
        </div>
      </div>

      {/* Tasks Grid */}
      {tasks.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
          <p className="mt-1 text-sm text-gray-500">
            No tasks match the current filters.
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onClick={() => onTaskClick?.(task)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
