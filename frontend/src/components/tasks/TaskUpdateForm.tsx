import { useState, useCallback } from 'react';

interface TaskUpdateFormProps {
  taskId: string;
  onSubmit: (content: string, isConcern: boolean) => void;
  onCancel: () => void;
  isLoading: boolean;
}

export function TaskUpdateForm({ taskId, onSubmit, onCancel, isLoading }: TaskUpdateFormProps) {
  const [content, setContent] = useState('');
  const [isConcern, setIsConcern] = useState(false);

  const isValid = content.trim().length > 0;

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || isLoading) return;
    onSubmit(content.trim(), isConcern);
  }, [content, isConcern, isValid, isLoading, onSubmit]);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="update-description" className="block text-sm font-medium text-gray-700">
          Update Description <span className="text-red-500">*</span>
        </label>
        <textarea
          id="update-description"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Describe your progress or concern..."
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          required
        />
      </div>

      <div className="flex items-center">
        <input
          id="need-help"
          type="checkbox"
          checked={isConcern}
          onChange={(e) => setIsConcern(e.target.checked)}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="need-help" className="ml-2 block text-sm text-gray-900">
          Need help / Have concern
        </label>
        <span className="ml-2 text-xs text-gray-500">
          (Flag this update for manager attention)
        </span>
      </div>

      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={!isValid || isLoading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Submitting...
            </>
          ) : (
            'Submit Update'
          )}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 bg-gray-200 hover:bg-gray-300 disabled:opacity-50 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

export default TaskUpdateForm;
