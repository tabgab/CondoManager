import type { Task } from '../../types';

interface TaskCardProps {
  task: Task;
  onClick?: (task: Task) => void;
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  on_hold: 'bg-orange-100 text-orange-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  verified: 'bg-purple-100 text-purple-800',
};

const priorityColors: Record<string, string> = {
  low: 'bg-gray-100 text-gray-800',
  normal: 'bg-blue-100 text-blue-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800',
};

export function TaskCard({ task, onClick }: TaskCardProps) {
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed' && task.status !== 'cancelled';

  return (
    <div
      onClick={() => onClick?.(task)}
      className="bg-white rounded-lg shadow border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-medium text-gray-900 truncate">
              {task.title}
            </h3>
            {isOverdue && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                Overdue
              </span>
            )}
          </div>
          <p className="mt-1 text-xs text-gray-500 line-clamp-2">
            {task.description || 'No description'}
          </p>
        </div>
        <div className="ml-4 flex-shrink-0 flex flex-col items-end gap-1">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
              statusColors[task.status] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {task.status.replace('_', ' ')}
          </span>
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
              priorityColors[task.priority] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {task.priority}
          </span>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-gray-500">
        {task.assignee && (
          <div className="flex items-center">
            <svg
              className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <span className="truncate">
              {task.assignee.first_name} {task.assignee.last_name}
            </span>
          </div>
        )}

        {task.due_date && (
          <div className="flex items-center">
            <svg
              className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
              {new Date(task.due_date).toLocaleDateString()}
            </span>
          </div>
        )}

        {task.estimated_hours && (
          <div className="flex items-center">
            <svg
              className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{task.estimated_hours}h estimated</span>
          </div>
        )}
      </div>

      {task.building && (
        <div className="mt-2 text-xs text-gray-500">
          <span className="font-medium">Building:</span> {task.building.name}
          {task.apartment && (
            <span> • Unit {task.apartment.unit_number}</span>
          )}
        </div>
      )}
    </div>
  );
}

export default TaskCard;
