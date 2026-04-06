import type { TaskUpdate } from '../../types';

interface TaskMessageThreadProps {
  updates: TaskUpdate[];
}

export function TaskMessageThread({ updates }: TaskMessageThreadProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMessageStyle = (userType: string, isConcern: boolean) => {
    if (userType === 'manager') {
      return 'bg-blue-50 border-l-4 border-blue-500';
    }
    if (userType === 'system') {
      return 'bg-gray-100 border-l-4 border-gray-400';
    }
    return isConcern 
      ? 'bg-red-50 border-l-4 border-red-500' 
      : 'bg-gray-50 border-l-4 border-gray-300';
  };

  const getSenderLabel = (userType: string) => {
    if (userType === 'manager') return 'Manager';
    if (userType === 'employee') return 'Employee';
    if (userType === 'system') return 'System';
    return userType;
  };

  const getSenderBadgeColor = (userType: string) => {
    if (userType === 'manager') return 'bg-blue-100 text-blue-800';
    if (userType === 'employee') return 'bg-green-100 text-green-800';
    if (userType === 'system') return 'bg-gray-200 text-gray-700';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-4">
      {updates.length === 0 ? (
        <div className="text-center py-6 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No updates yet</p>
          <p className="text-sm text-gray-400 mt-1">
            Updates and messages will appear here when the employee makes progress
          </p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
          {updates.map((update) => (
            <div
              key={update.id}
              className={`p-4 rounded-lg ${getMessageStyle(update.user_type, update.is_concern)}`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded ${getSenderBadgeColor(update.user_type)}`}>
                    {getSenderLabel(update.user_type)}
                  </span>
                  {update.is_concern && (
                    <span className="text-xs font-medium px-2 py-0.5 rounded bg-red-100 text-red-800">
                      Concern
                    </span>
                  )}
                  <time className="text-xs text-gray-500">
                    {formatDate(update.created_at)}
                  </time>
                </div>
              </div>
              <p className="text-sm text-gray-800 whitespace-pre-wrap">
                {update.content}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TaskMessageThread;
