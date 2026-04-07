import type { ReportMessage, Report } from '../../types';

interface ReportMessageThreadProps {
  report: Report;
  messages: ReportMessage[];
}

export function ReportMessageThread({ report, messages }: ReportMessageThreadProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMessageStyle = (senderType: string) => {
    if (senderType === 'manager') {
      return 'bg-blue-50 border-l-4 border-blue-500';
    }
    return 'bg-gray-50 border-l-4 border-gray-300';
  };

  const getSenderLabel = (senderType: string, isOwner: boolean) => {
    if (senderType === 'manager') {
      return 'Manager';
    }
    return isOwner ? 'You' : senderType;
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-900">Conversation</h3>

      {messages.length === 0 ? (
        <div className="text-center py-6 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No messages yet</p>
          <p className="text-sm text-gray-400 mt-1">The management will respond soon</p>
        </div>
      ) : (
        <div className="space-y-4 max-h-80 overflow-y-auto">
          {messages.map((message) => {
            const isOwnerMessage = message.sender_type === 'owner' || message.sender_id === report.submitted_by_id;
            const isManagerMessage = message.sender_type === 'manager';

            return (
              <div
                key={message.id}
                className={`p-4 rounded-lg ${getMessageStyle(message.sender_type)}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded ${
                        isManagerMessage
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {getSenderLabel(message.sender_type, isOwnerMessage)}
                    </span>
                    <time className="text-xs text-gray-500">
                      {formatDate(message.created_at)}
                    </time>
                  </div>
                </div>
                <p className="text-sm text-gray-800 whitespace-pre-wrap">
                  {message.content}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default ReportMessageThread;
