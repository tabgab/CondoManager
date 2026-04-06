import { X } from 'lucide-react';
import type { Report, ReportMessage } from '../../types';
import { ReportTimeline } from './ReportTimeline';
import { ReportMessageThread } from './ReportMessageThread';

interface ReportDetailModalProps {
  report: Report;
  messages?: ReportMessage[];
  isOpen: boolean;
  onClose: () => void;
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  acknowledged: 'bg-blue-100 text-blue-800',
  task_created: 'bg-purple-100 text-purple-800',
  rejected: 'bg-red-100 text-red-800',
  resolved: 'bg-green-100 text-green-800',
};

const priorityColors: Record<string, string> = {
  low: 'bg-gray-100 text-gray-800',
  medium: 'bg-blue-100 text-blue-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800',
};

export function ReportDetailModal({ report, messages = [], isOpen, onClose }: ReportDetailModalProps) {
  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
        <div className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-3xl">
          {/* Header */}
          <div className="bg-gray-50 px-4 py-3 sm:px-6 flex items-center justify-between border-b">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Report #{report.id}</h3>
              <p className="text-sm text-gray-500">Submitted on {formatDate(report.created_at)}</p>
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
          <div className="px-4 py-5 sm:p-6 space-y-6">
            {/* Report Info */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">{report.title}</h2>
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[report.status]}`}>
                    {report.status}
                  </span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColors[report.priority]}`}>
                    {report.priority}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
                <div>
                  <span className="font-medium">Category:</span> {report.category || 'Not specified'}
                </div>
                {report.building_id && (
                  <div>
                    <span className="font-medium">Building:</span> {report.building_id}
                  </div>
                )}
                {report.apartment_id && (
                  <div>
                    <span className="font-medium">Apartment:</span> {report.apartment_id}
                  </div>
                )}
                {report.assigned_to && (
                  <div>
                    <span className="font-medium">Assigned to:</span> {report.assigned_to}
                  </div>
                )}
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-800 whitespace-pre-wrap">{report.description}</p>
              </div>
            </div>

            {/* Timeline */}
            <div className="border-t pt-4">
              <ReportTimeline report={report} />
            </div>

            {/* Message Thread */}
            <div className="border-t pt-4">
              <ReportMessageThread report={report} messages={messages} />
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

export default ReportDetailModal;
