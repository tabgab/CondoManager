import type { Report } from '../../types';

interface ReportCardProps {
  report: Report;
  onClick?: (report: Report) => void;
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  acknowledged: 'bg-blue-100 text-blue-800',
  task_created: 'bg-purple-100 text-purple-800',
  rejected: 'bg-red-100 text-red-800',
  resolved: 'bg-green-100 text-green-800',
  deleted: 'bg-gray-100 text-gray-800',
};

const priorityColors: Record<string, string> = {
  low: 'bg-gray-100 text-gray-800',
  normal: 'bg-blue-100 text-blue-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800',
};

export function ReportCard({ report, onClick }: ReportCardProps) {
  return (
    <div
      onClick={() => onClick?.(report)}
      className="bg-white rounded-lg shadow border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-gray-900 truncate">
            {report.title}
          </h3>
          <p className="mt-1 text-xs text-gray-500 line-clamp-2">
            {report.description}
          </p>
        </div>
        <div className="ml-4 flex-shrink-0 flex flex-col items-end gap-1">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
              statusColors[report.status] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {report.status.replace('_', ' ')}
          </span>
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
              priorityColors[report.priority] || 'bg-gray-100 text-gray-800'
            }`}
          >
            {report.priority}
          </span>
        </div>
      </div>

      <div className="mt-3 flex items-center text-xs text-gray-500">
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
          {report.reporter?.first_name} {report.reporter?.last_name}
        </span>
        <span className="mx-2">•</span>
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
        <span>{new Date(report.created_at).toLocaleDateString()}</span>
      </div>

      {report.building && (
        <div className="mt-2 text-xs text-gray-500">
          <span className="font-medium">Building:</span> {report.building.name}
          {report.apartment && (
            <span> • Unit {report.apartment.unit_number}</span>
          )}
        </div>
      )}

      {report.messages?.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <span className="text-xs text-gray-500">
            {report.messages.length} message{report.messages.length !== 1 ? 's' : ''}
          </span>
        </div>
      )}
    </div>
  );
}

export default ReportCard;
