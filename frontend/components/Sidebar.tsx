'use client';

import { motion } from 'framer-motion';
import {
  Images,
  Users,
  Tags,
  Star,
  Trash2,
  FolderOpen,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useGalleryStore } from '@/lib/store';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function Sidebar({ activeSection, onSectionChange }: SidebarProps) {
  const { stats, clusters, categories } = useGalleryStore();

  const menuItems = [
    {
      id: 'all',
      label: 'All Photos',
      icon: Images,
      count: stats?.total_photos || 0,
    },
    {
      id: 'people',
      label: 'People',
      icon: Users,
      count: stats?.total_people || 0,
    },
    {
      id: 'objects',
      label: 'Objects',
      icon: Tags,
      count: categories?.length || 0,
    },
    {
      id: 'favorites',
      label: 'Favorites',
      icon: Star,
      count: 0,
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0 },
  };

  return (
    <aside className="w-64 lg:w-72 flex-shrink-0 hidden lg:block">
      <div className="sticky top-24 space-y-6">
        {/* Main Navigation */}
        <motion.nav
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="space-y-1"
        >
          {menuItems.map((item) => (
            <motion.button
              key={item.id}
              variants={itemVariants}
              onClick={() => onSectionChange(item.id)}
              className={cn(
                'w-full flex items-center justify-between px-4 py-3 rounded-xl',
                'transition-all duration-200 group',
                activeSection === item.id
                  ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20'
                  : 'text-gallery-muted hover:text-white hover:bg-gallery-surface'
              )}
            >
              <div className="flex items-center gap-3">
                <item.icon
                  className={cn(
                    'w-5 h-5 transition-transform group-hover:scale-110',
                    activeSection === item.id && 'text-orange-400'
                  )}
                />
                <span className="font-medium">{item.label}</span>
              </div>
              <span
                className={cn(
                  'text-sm px-2 py-0.5 rounded-full',
                  activeSection === item.id
                    ? 'bg-orange-500/20 text-orange-400'
                    : 'bg-gallery-surface text-gallery-muted'
                )}
              >
                {item.count}
              </span>
            </motion.button>
          ))}
        </motion.nav>

        {/* People Quick Access */}
        {clusters && clusters.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-3"
          >
            <div className="flex items-center justify-between px-4">
              <h3 className="text-sm font-semibold text-gallery-muted uppercase tracking-wider">
                People
              </h3>
              <button className="text-xs text-orange-400 hover:text-orange-300">
                View all
              </button>
            </div>
            <div className="space-y-1">
              {clusters.slice(0, 5).map((cluster, index) => (
                <button
                  key={cluster.id}
                  className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-gallery-muted hover:text-white hover:bg-gallery-surface transition-all group"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500/20 to-orange-600/20 flex items-center justify-center text-xs font-medium text-orange-400">
                    {cluster.name?.charAt(0) || `P${index + 1}`}
                  </div>
                  <span className="flex-1 text-left text-sm truncate">
                    {cluster.name || `Person ${index + 1}`}
                  </span>
                  <span className="text-xs text-gallery-muted">
                    {cluster.face_count}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Categories Quick Access */}
        {categories && categories.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-3"
          >
            <div className="flex items-center justify-between px-4">
              <h3 className="text-sm font-semibold text-gallery-muted uppercase tracking-wider">
                Categories
              </h3>
              <button className="text-xs text-orange-400 hover:text-orange-300">
                View all
              </button>
            </div>
            <div className="flex flex-wrap gap-2 px-4">
              {categories.slice(0, 8).map((category) => (
                <button
                  key={category.name}
                  className={cn(
                    'px-3 py-1.5 rounded-full text-xs font-medium',
                    'bg-gallery-surface border border-gallery-border',
                    'text-gallery-muted hover:text-white hover:border-orange-500/30',
                    'transition-all duration-200'
                  )}
                >
                  {category.name}
                  <span className="ml-1.5 text-gallery-muted/60">
                    {category.count}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* AI Features Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mx-2 p-4 rounded-2xl bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20"
        >
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-orange-500/20">
              <Sparkles className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <h4 className="font-semibold text-sm">AI-Powered</h4>
              <p className="text-xs text-gallery-muted mt-1">
                Face recognition, object detection & semantic search
              </p>
            </div>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-2 text-center">
            <div className="p-2 rounded-lg bg-gallery-bg/50">
              <div className="text-lg font-bold text-orange-400">YOLO</div>
              <div className="text-[10px] text-gallery-muted">Detection</div>
            </div>
            <div className="p-2 rounded-lg bg-gallery-bg/50">
              <div className="text-lg font-bold text-orange-400">Face</div>
              <div className="text-[10px] text-gallery-muted">Recognition</div>
            </div>
            <div className="p-2 rounded-lg bg-gallery-bg/50">
              <div className="text-lg font-bold text-orange-400">CLIP</div>
              <div className="text-[10px] text-gallery-muted">Search</div>
            </div>
          </div>
        </motion.div>
      </div>
    </aside>
  );
}
