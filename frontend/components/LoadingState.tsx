'use client';

import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-32">
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          rotate: [0, 5, -5, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="relative"
      >
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
          <Sparkles className="w-8 h-8 text-white" />
        </div>
        <div className="absolute -inset-2 rounded-2xl bg-orange-500/20 blur-xl -z-10 animate-pulse" />
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-6 text-center"
      >
        <h3 className="text-lg font-semibold">Loading your gallery</h3>
        <p className="text-sm text-gallery-muted mt-1">
          Fetching photos and AI insights...
        </p>
      </motion.div>

      {/* Loading dots */}
      <div className="flex gap-1.5 mt-6">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2 h-2 rounded-full bg-orange-500"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
            }}
          />
        ))}
      </div>
    </div>
  );
}

export function PhotoGridSkeleton() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="aspect-square rounded-2xl shimmer"
          style={{ animationDelay: `${i * 100}ms` }}
        />
      ))}
    </div>
  );
}
