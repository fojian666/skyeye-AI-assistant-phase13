import { useState } from 'react';
import { motion } from 'motion/react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
}

export function ChatInput({ onSendMessage }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          className="
            w-full px-6 py-4 pr-14 rounded-3xl
            backdrop-blur-xl bg-white/10 border border-white/20
            placeholder-gray-500 text-gray-800
            focus:outline-none focus:ring-2 focus:ring-blue-500/50
            focus:border-blue-500/30 focus:bg-white/15
            transition-all duration-200
            shadow-lg shadow-black/5
          "
        />
        <motion.button
          type="submit"
          disabled={!message.trim()}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="
            absolute right-3 top-1/2 -translate-y-1/2
            w-8 h-8 rounded-full
            bg-blue-500/80 hover:bg-blue-500
            disabled:bg-gray-400/50 disabled:cursor-not-allowed
            backdrop-blur-xl border border-white/20
            flex items-center justify-center
            transition-all duration-200
            shadow-lg shadow-blue-500/20
          "
        >
          <Send className="w-4 h-4 text-white" />
        </motion.button>
      </div>
    </form>
  );
}