import React from 'react';
import { motion } from 'framer-motion';

export const LoadingBubbles: React.FC = () => {
  const numBubbles = 3;
  const duration = 0.9;
  const stagger = 0.18;

  return (
    <div className="flex gap-1.5 py-3 min-w-[60px] items-end" aria-label="Loading...">
      {Array.from({ length: numBubbles }).map((_, i) => (
        <motion.div
          key={i}
          className="w-2 h-2 rounded-full bg-neutral-500 dark:bg-gold-600"
          initial={{ y: 0 }}
          animate={{ y: [0, -8, 0] }}
          transition={{
            duration,
            repeat: Infinity,
            repeatType: 'loop',
            ease: 'easeInOut',
            delay: i * stagger,
          }}
          aria-hidden="true"
        />
      ))}
    </div>
  );
};
