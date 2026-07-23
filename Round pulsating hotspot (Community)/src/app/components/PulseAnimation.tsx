import { motion } from 'motion/react';

export function PulseAnimation() {
  return (
    <div className="relative flex items-center justify-center">
      {/* Main blue circle */}
      <motion.div
        className="w-16 h-16 bg-blue-500 rounded-full"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [1, 0.8, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Outer pulse ring */}
      <motion.div
        className="absolute w-20 h-20 border-2 border-blue-400 rounded-full"
        animate={{
          scale: [1, 1.5, 1],
          opacity: [0.7, 0, 0.7],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Additional outer pulse ring for more effect */}
      <motion.div
        className="absolute w-24 h-24 border border-blue-300 rounded-full"
        animate={{
          scale: [1, 1.8, 1],
          opacity: [0.5, 0, 0.5],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.5,
        }}
      />
    </div>
  );
}