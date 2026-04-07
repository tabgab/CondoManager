import type { Task, TaskUpdate } from '../../types';

interface TaskDetailProps {
  task: Task;
  updates: TaskUpdate[];
  onClose: () => void;
  onComplete: () => void;
  onAddUpdate: () => void;
  isLoading: boolean;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800';
    case 'in_progress':
      return 'bg-blue-100 text-blue-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'verified':
      return 'bg-purple-100 text-purple-800';
    case 'on_hold':
      return 'bg-orange-100 text-orange-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-100 text-red-800';
    case 'high':
      return 'bg-orange-100 text-orange-800';
    case 'normal':
      return 'bg-blue-100 text-blue-800';
    case 'low':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export function TaskDetail({ task, updates, onClose, onComplete, onAddUpdate, isLoading }: TaskDetailProps) {
  const canComplete = task.status === 'in_progress' || task.status === 'pending';

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-start">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">{task.title}</h2>
          <div className="flex gap-2 mt-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(task.status)}`}>
              {task.status.replace('_', ' ')}
            </span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getPriorityColor(task.priority)}`}>
              {task.priority}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
          aria-label="Close"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Body */}
      <div className="px-6 py-4 space-y-4">
        {/* Description */}
        <div>
          <h3 className="text-sm font-medium text-gray-900">Description</h3>
          <p className="mt-1 text-sm text-gray-600">{task.description}</p>
        </div>

        {/* Task Info */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          {task.due_date && (
            <div>
              <span className="font-medium text-gray-900">Due Date: </span>
              <span className="text-gray-600">{new Date(task.due_date).toLocaleDateString()}</span>
            </div>
          )}
          {task.estimated_hours && (
            <div>
              <span className="font-medium text-gray-900">Est. Hours: </span>
              <span className="text-gray-600">{task.estimated_hours}</span>
            </div>
          )}
          {task.building && (
            <div>
              <span className="font-medium text-gray-900">Building: </span>
              <span className="text-gray-600">{task.building.name}</span>
            </div>
          )}
          {task.apartment && (
            <div>
              <span className="font-medium text-gray-900">Unit: </span>
              <span className="text-gray-600">{task.apartment.unit_number}</span>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          {canComplete && (
            <button
              onClick={onComplete}
              disabled={isLoading}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              {isLoading ? 'Completing...' : 'Mark Complete'}
            </button>
          )}
          <button
            onClick={onAddUpdate}
            disabled={isLoading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Add Update
          </button>
        </div>

        {/* Updates History */}
        {updates.length > 0 && (
          <div className="pt-4 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Activity History</h3>
            <div className="space-y-3">
              {updates.map((update) => (
                <div key={update.id} className="flex gap-3">
                  <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${update.update_type === 'concern' ? 'bg-red-500' : 'bg-blue-500'}`} />
                  <div className="flex-1">
                    <p className="text-sm text-gray-700">{update.content}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(update.created_at).toLocaleString()} {update.update_type === 'concern' && '• Flagged as concern'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {updates.length === 0 && (
          <div className="pt-4 border-t border-gray-200 text-center py-4">
            <p className="text-sm text-gray-500">No updates yet</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default TaskDetail;
