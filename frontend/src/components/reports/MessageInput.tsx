import { useState } from 'react';

interface MessageInputProps {
  onSubmit: (content: string) => Promise<void>;
}

export function MessageInput({ onSubmit }: MessageInputProps) {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const MAX_LENGTH = 1000;
  const charCount = content.length;
  const isEmpty = !content.trim();
  const isOverLimit = charCount > MAX_LENGTH;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isEmpty || isOverLimit || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await onSubmit(content.trim());
      setContent('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Type a message..."
          maxLength={MAX_LENGTH}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          disabled={isSubmitting}
        />
        <div className="absolute bottom-2 right-2 text-xs text-gray-400">
          {charCount}/{MAX_LENGTH}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className={`text-sm ${isOverLimit ? 'text-red-600' : 'text-gray-500'}`}>
          {isOverLimit ? 'Character limit exceeded' : `${charCount} characters`}
        </span>

        <button
          type="submit"
          disabled={isEmpty || isOverLimit || isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? 'Sending...' : 'Send'}
        </button>
      </div>
    </form>
  );
}

export default MessageInput;
