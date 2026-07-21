import { useState, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ChatHeader } from './ChatHeader';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

const initialMessages: Message[] = [
  {
    id: '1',
    text: 'Hello! I\'m your AI assistant. How can I help you today?',
    isUser: false,
    timestamp: '2:30 PM'
  },
  {
    id: '2',
    text: 'Hi! Can you tell me about the new iOS 26 features?',
    isUser: true,
    timestamp: '2:31 PM'
  },
  {
    id: '3',
    text: 'iOS 26 introduces the revolutionary Liquid Glass design system with advanced glassmorphism effects, fluid animations, and enhanced AR integration. The interface feels more organic and responsive than ever before!',
    isUser: false,
    timestamp: '2:31 PM'
  }
];

// Simple bot responses for demonstration
const botResponses = [
  "That's a great question! Let me think about that...",
  "I'd be happy to help you with that. Here's what I know:",
  "Interesting! From my perspective, I think:",
  "That's a fascinating topic. In my experience:",
  "I understand what you're asking. Here's my take:",
  "Great point! I've been thinking about this too:",
];

export function Chatbot() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (text: string) => {
    const now = new Date();
    const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp
    };

    setMessages(prev => [...prev, userMessage]);

    // Simulate bot response
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponses[Math.floor(Math.random() * botResponses.length)],
        isUser: false,
        timestamp
      };
      setMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="
        w-full max-w-4xl mx-auto h-[80vh] flex flex-col
        backdrop-blur-xl bg-white/5 border border-white/10
        rounded-3xl shadow-2xl shadow-black/10
        overflow-hidden
        before:absolute before:inset-0 before:rounded-3xl
        before:bg-gradient-to-br before:from-white/5 before:to-transparent
        before:pointer-events-none relative
      "
    >
      <div className="relative z-10 flex flex-col h-full">
        <div className="p-6 pb-0">
          <ChatHeader />
        </div>
        
        <div className="flex-1 overflow-y-auto px-6 py-4 scroll-smooth">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message.text}
              isUser={message.isUser}
              timestamp={message.timestamp}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="p-6 pt-4">
          <ChatInput onSendMessage={handleSendMessage} />
        </div>
      </div>
    </motion.div>
  );
}