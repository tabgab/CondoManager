import { useState } from 'react';
import { X, CheckCircle, AlertCircle } from 'lucide-react';
import type { Task, User } from '../../types';
import { TaskAssignmentControls } from './TaskAssignmentControls';
import { TaskMessageThread } from './TaskMessageThread';
import { TaskMessageInput } from './TaskMessageInput';

interface ManagerTaskDetailProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  employees: User[];
  messages?: Task['updates'];
  onAssign?: (employeeId: string) => void;
  onUnassign?: () => void;
  onMarkComplete?: () => void;
  onVerify?: () => void;
  onSendMessage?: (content: string) => void;
  isAssigning?: boolean;
  isCompleting?: boolean;
  isVerifying?: boolean;
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  on_hold: 'bg-orange-100 text-orange-800',
  completed: 'bg-green-100 text-green-800',
  verified: 'bg-purple-100 text-purple-800',
  cancelled: 'bg-red-100 text-red-800',
};

const priorityColors: Record<string, string> = {
  low: 'bg-gray-100 text-gray-800',
  medium: 'bg-blue-100 text-blue-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800',
};

export function ManagerTaskDetail({
  task,
  isOpen,
  onClose,
  employees,
  messages = [],
  onAssign,
  onUnassign,
  onMarkComplete,
  onVerify,
  onSendMessage,
  isAssigning,
  isCompleting,
  isVerifying,
}: ManagerTaskDetailProps) {
  const [messageContent, setMessageContent] = useState('');

  if (!isOpen || !task) return null;

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleSendMessage = async (content: string) => {
    if (onSendMessage) {
      await onSendMessage(content);
      setMessageContent('');
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

      <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
        <div className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl">
          {/* Header */}
          <div className="bg-gray-50 px-4 py-3 sm:px-6 flex items-center justify-between border-b">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-medium text-gray-900">Task #{task.id}</h3>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[task.status]}`}>
                {task.status.replace('_', ' ')}
              </span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColors[task.priority]}`}>
                {task.priority}
              </span>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
              aria-label="Close"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="px-4 py-5 sm:p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column - Task Info */}
              <div className="space-y-6">
                {/* Title & Description */}
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-2">{task.title}</h2>
                  <p className="text-gray-600 whitespace-pre-wrap">{task.description}</p>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Due Date:</span>
                    <p className="font-medium text-gray-900">{formatDate(task.due_date)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Estimated Hours:</span>
                    <p className="font-medium text-gray-900">{task.estimated_hours || 'Not set'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Building:</span>
                    <p className="font-medium text-gray-900">{task.building_id || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Apartment:</span>
                    <p className="font-medium text-gray-900">{task.apartment_id || 'N/A'}</p>
                  </div>
                </div>

                {/* Assignment Controls */}
                <div className="border-t pt-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Assignment</h3>
                  <TaskAssignmentControls
                    employees={employees}
                    currentAssigneeId={task.assignee_id || null}
                    onAssign={(id) => onAssign?.(id)}
                    onUnassign={() => onUnassign?.()}
                    isAssigning={isAssigning}
                  />
                </div>

                {/* Related Report Link */}
                {task.report_id && (
                  <div className="border-t pt-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Related Report</h3>
                    <a
                      href={`/reports/${task.report_id}`}
                      className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
                    >
                      <AlertCircle className="h-4 w-4" />
                      View Report #{task.report_id}
                    </a>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="border-t pt-4 flex gap-3">
                  {task.status === 'in_progress' && (
                    <button
                      onClick={onMarkComplete}
                      disabled={isCompleting}
                      className="flex-1 inline-flex justify-center items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      {isCompleting ? 'Completing...' : 'Mark as Complete'}
                    </button>
                  )}
                  {task.status === 'completed' && (
                    <button
                      onClick={onVerify}
                      disabled={isVerifying}
                      className="flex-1 inline-flex justify-center items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                    >
                      {isVerifying ? 'Verifying...' : 'Verify Completion'}
                    </button>
                  )}
                </div>
              </div>

              {/* Right Column - Messages */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-3">Messages</h3>
                  <p className="text-sm text-gray-500 mb-4">Conversation with employee</p>
                  <TaskMessageThread updates={messages} />
                </div>

                {/* Message Input */}
                {task.status !== 'verified' && task.status !== 'cancelled' && (
                  <div className="border-t pt-4">
                    <TaskMessageInput onSubmit={handleSendMessage} />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              onClick={onClose}
              className="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ManagerTaskDetail;
