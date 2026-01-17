'use client';

import { motion } from 'framer-motion';
import { Images, Users, Tag, HardDrive, Sparkles, TrendingUp } from 'lucide-react';
import { cn, formatBytes } from '@/lib/utils';
import { useGalleryStore } from '@/lib/store';

export function StatsCards() {
  const { stats } = useGalleryStore();

  if (!stats) return null;

  const cards = [
    {
      label: 'Total Photos',
      value: stats.total_photos,
      icon: Images,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      textColor: 'text-blue-400',
    },
    {
      label: 'People Detected',
      value: stats.total_people,
      icon: Users,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      textColor: 'text-purple-400',
    },
    {
      label: 'Object Categories',
      value: Object.keys(stats.categories || {}).length,
      icon: Tag,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      textColor: 'text-green-400',
    },
    {
      label: 'Storage Used',
      value: formatBytes(stats.storage_used || 0),
      icon: HardDrive,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      textColor: 'text-orange-400',
      isText: true,
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <motion.div
          key={card.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={cn(
            'relative p-5 rounded-2xl',
            'bg-gallery-surface border border-gallery-border',
            'hover:border-gallery-border/80 transition-all duration-300',
            'group overflow-hidden'
          )}
        >
          {/* Background gradient on hover */}
          <div
            className={cn(
              'absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300',
              card.bgColor
            )}
          />

          <div className="relative z-10">
            <div className="flex items-start justify-between">
              <div
                className={cn(
                  'p-2.5 rounded-xl',
                  card.bgColor
                )}
              >
                <card.icon className={cn('w-5 h-5', card.textColor)} />
              </div>
              <TrendingUp className="w-4 h-4 text-gallery-muted opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>

            <div className="mt-4">
              <p className="text-2xl font-bold">
                {card.isText ? card.value : card.value.toLocaleString()}
              </p>
              <p className="text-sm text-gallery-muted mt-1">{card.label}</p>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
