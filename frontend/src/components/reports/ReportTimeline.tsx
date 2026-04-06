import type { Report } from '../../types';

interface ReportTimelineProps {
  report: Report;
}

interface TimelineEvent {
  id: string;
  status: string;
  date: string;
  label: string;
  description?: string;
  isCurrent: boolean;
}

const statusColors: Record<string, string> = {
  submitted: 'bg-blue-500',
  acknowledged: 'bg-blue-600',
  task_created: 'bg-purple-500',
  rejected: 'bg-red-500',
  resolved: 'bg-green-500',
  pending: 'bg-yellow-500',
};

const statusIcons: Record<string, string> = {
  submitted: '📝',
  acknowledged: '✓',
  task_created: '🔧',
  rejected: '✕',
  resolved: '✓',
  pending: '⏳',
};

export function ReportTimeline({ report }: ReportTimelineProps) {
  const events: TimelineEvent[] = [];

  // Always add submission event
  events.push({
    id: 'submitted',
    status: 'submitted',
    date: report.created_at,
    label: 'Report Submitted',
    description: 'Your report has been submitted to the management.',
    isCurrent: report.status === 'pending',
  });

  // Add acknowledgment event if status is past pending
  if (report.status !== 'pending' && report.acknowledged_at) {
    events.push({
      id: 'acknowledged',
      status: 'acknowledged',
      date: report.acknowledged_at,
      label: 'Acknowledged by Manager',
      description: 'A manager has reviewed your report.',
      isCurrent: report.status === 'acknowledged',
    });
  }

  // Add task creation if applicable
  if (report.status === 'task_created' || report.status === 'resolved') {
    events.push({
      id: 'task_created',
      status: 'task_created',
      date: report.updated_at,
      label: 'Task Created',
      description: 'A work task has been created from this report.',
      isCurrent: report.status === 'task_created',
    });
  }

  // Add rejection if applicable
  if (report.status === 'rejected') {
    events.push({
      id: 'rejected',
      status: 'rejected',
      date: report.updated_at,
      label: 'Report Rejected',
      description: report.rejection_reason || 'This report was not accepted.',
      isCurrent: true,
    });
  }

  // Add resolution if applicable
  if (report.status === 'resolved') {
    events.push({
      id: 'resolved',
      status: 'resolved',
      date: report.resolved_at || report.updated_at,
      label: 'Resolved',
      description: report.resolution_note || 'The issue has been resolved.',
      isCurrent: true,
    });
  }

  // Sort events by date
  events.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-4" role="list">
      <h3 className="text-sm font-medium text-gray-900" role="heading" aria-level={3}>Current Status</h3>
      
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

        {/* Events */}
        <div className="space-y-6">
          {events.map((event, index) => (
            <div key={event.id} className="relative flex gap-4" role="listitem">
              {/* Status dot */}
              <div
                className={`relative z-10 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                  statusColors[event.status] || 'bg-gray-400'
                } ${event.isCurrent ? 'ring-4 ring-blue-100' : ''}`}
              >
                <span className="text-white">{statusIcons[event.status]}</span>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 pt-1">
                <div className="flex items-center justify-between">
                  <p className={`text-sm font-medium ${event.isCurrent ? 'text-blue-600' : 'text-gray-900'}`}>
                    {event.label}
                    {event.isCurrent && (
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        Current Status
                      </span>
                    )}
                  </p>
                  <time className="text-xs text-gray-500">
                    {formatDate(event.date)}
                  </time>
                </div>
                {event.description && (
                  <p className="mt-1 text-sm text-gray-600">{event.description}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ReportTimeline;
