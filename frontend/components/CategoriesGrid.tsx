'use client';

import { motion } from 'framer-motion';
import { Tag, ChevronRight, Package } from 'lucide-react';
import { cn, capitalizeFirst } from '@/lib/utils';
import { useGalleryStore } from '@/lib/store';
import type { Category } from '@/types';

// Category icons mapping
const categoryIcons: Record<string, string> = {
  person: '👤',
  car: '🚗',
  dog: '🐕',
  cat: '🐱',
  bird: '🐦',
  bicycle: '🚲',
  motorcycle: '🏍️',
  airplane: '✈️',
  bus: '🚌',
  train: '🚂',
  truck: '🚚',
  boat: '⛵',
  traffic_light: '🚦',
  fire_hydrant: '🧯',
  stop_sign: '🛑',
  bench: '🪑',
  elephant: '🐘',
  bear: '🐻',
  zebra: '🦓',
  giraffe: '🦒',
  backpack: '🎒',
  umbrella: '☂️',
  handbag: '👜',
  tie: '👔',
  suitcase: '🧳',
  frisbee: '🥏',
  skis: '🎿',
  snowboard: '🏂',
  sports_ball: '⚽',
  kite: '🪁',
  baseball_bat: '⚾',
  skateboard: '🛹',
  surfboard: '🏄',
  tennis_racket: '🎾',
  bottle: '🍾',
  wine_glass: '🍷',
  cup: '☕',
  fork: '🍴',
  knife: '🔪',
  spoon: '🥄',
  bowl: '🥣',
  banana: '🍌',
  apple: '🍎',
  sandwich: '🥪',
  orange: '🍊',
  broccoli: '🥦',
  carrot: '🥕',
  hot_dog: '🌭',
  pizza: '🍕',
  donut: '🍩',
  cake: '🎂',
  chair: '🪑',
  couch: '🛋️',
  potted_plant: '🪴',
  bed: '🛏️',
  dining_table: '🍽️',
  toilet: '🚽',
  tv: '📺',
  laptop: '💻',
  mouse: '🖱️',
  remote: '📱',
  keyboard: '⌨️',
  cell_phone: '📱',
  microwave: '📦',
  oven: '🍳',
  toaster: '🍞',
  sink: '🚰',
  refrigerator: '🧊',
  book: '📚',
  clock: '🕐',
  vase: '🏺',
  scissors: '✂️',
  teddy_bear: '🧸',
  hair_drier: '💨',
  toothbrush: '🪥',
};

interface CategoriesGridProps {
  onCategoryClick: (category: Category) => void;
}

export function CategoriesGrid({ onCategoryClick }: CategoriesGridProps) {
  const { categories } = useGalleryStore();

  if (!categories || categories.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center py-20"
      >
        <div className="w-20 h-20 rounded-2xl bg-gallery-surface flex items-center justify-center mb-4">
          <Package className="w-10 h-10 text-gallery-muted" />
        </div>
        <h3 className="text-xl font-semibold mb-2">No objects detected yet</h3>
        <p className="text-gallery-muted text-center max-w-md">
          Upload photos and our YOLO model will automatically detect and categorize objects.
        </p>
      </motion.div>
    );
  }

  // Sort by count
  const sortedCategories = [...categories].sort((a, b) => b.count - a.count);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
      {sortedCategories.map((category, index) => {
        const icon = categoryIcons[category.name.toLowerCase()] || '📦';
        
        return (
          <motion.button
            key={category.name}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.03 }}
            onClick={() => onCategoryClick(category)}
            className={cn(
              'group relative p-5 rounded-2xl',
              'bg-gallery-surface border border-gallery-border',
              'hover:border-orange-500/30 hover:shadow-lg hover:shadow-orange-500/5',
              'transition-all duration-300 text-left'
            )}
          >
            {/* Icon */}
            <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">
              {icon}
            </div>

            {/* Name */}
            <h3 className="font-semibold truncate">
              {capitalizeFirst(category.name)}
            </h3>
            
            {/* Count */}
            <div className="flex items-center gap-2 mt-2">
              <span className="px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-400 text-xs font-medium">
                {category.count} detection{category.count !== 1 && 's'}
              </span>
            </div>

            {/* Hover arrow */}
            <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <ChevronRight className="w-5 h-5 text-orange-400" />
            </div>
          </motion.button>
        );
      })}
    </div>
  );
}
