'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Upload,
  Grid3X3,
  LayoutGrid,
  Clock,
  Settings,
  Sparkles,
  Menu,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useGalleryStore } from '@/lib/store';
import type { ViewMode } from '@/types';

interface HeaderProps {
  onUploadClick: () => void;
}

export function Header({ onUploadClick }: HeaderProps) {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const { viewMode, setViewMode, searchQuery, setSearchQuery, stats } = useGalleryStore();

  const viewOptions: { mode: ViewMode; icon: React.ReactNode; label: string }[] = [
    { mode: 'grid', icon: <Grid3X3 className="w-4 h-4" />, label: 'Grid' },
    { mode: 'masonry', icon: <LayoutGrid className="w-4 h-4" />, label: 'Masonry' },
    { mode: 'timeline', icon: <Clock className="w-4 h-4" />, label: 'Timeline' },
  ];

  return (
    <header className="sticky top-0 z-50 glass border-b border-gallery-border">
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <motion.div 
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="absolute -inset-1 rounded-xl bg-orange-500/20 blur-lg -z-10" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold tracking-tight">
                Smart<span className="text-gradient">Gallery</span>
              </h1>
              {stats && (
                <p className="text-xs text-gallery-muted">
                  {stats.total_photos} photos • {stats.total_people} people
                </p>
              )}
            </div>
          </motion.div>

          {/* Search Bar - Desktop */}
          <motion.div 
            className="hidden md:flex flex-1 max-w-xl mx-8"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div
              className={cn(
                'relative w-full transition-all duration-300',
                isSearchFocused && 'scale-[1.02]'
              )}
            >
              <Search
                className={cn(
                  'absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors',
                  isSearchFocused ? 'text-orange-400' : 'text-gallery-muted'
                )}
              />
              <input
                type="text"
                placeholder="Search photos, people, objects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setIsSearchFocused(false)}
                className={cn(
                  'w-full pl-11 pr-4 py-3 rounded-xl',
                  'bg-gallery-surface border border-gallery-border',
                  'text-sm placeholder:text-gallery-muted',
                  'focus:outline-none focus:border-orange-500/50 focus:ring-2 focus:ring-orange-500/20',
                  'transition-all duration-300'
                )}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gallery-muted hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </motion.div>

          {/* Actions - Desktop */}
          <motion.div 
            className="hidden md:flex items-center gap-2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            {/* View Mode Toggle */}
            <div className="flex items-center p-1 rounded-lg bg-gallery-surface border border-gallery-border">
              {viewOptions.map((option) => (
                <button
                  key={option.mode}
                  onClick={() => setViewMode(option.mode)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all',
                    viewMode === option.mode
                      ? 'bg-orange-500/20 text-orange-400'
                      : 'text-gallery-muted hover:text-white'
                  )}
                  title={option.label}
                >
                  {option.icon}
                </button>
              ))}
            </div>

            {/* Upload Button */}
            <button
              onClick={onUploadClick}
              className={cn(
                'flex items-center gap-2 px-5 py-2.5 rounded-xl',
                'bg-gradient-to-r from-orange-500 to-orange-600',
                'text-white font-medium text-sm',
                'hover:from-orange-600 hover:to-orange-700',
                'transition-all duration-300',
                'shadow-lg shadow-orange-500/25 hover:shadow-orange-500/40',
                'active:scale-95'
              )}
            >
              <Upload className="w-4 h-4" />
              <span>Upload</span>
            </button>

            {/* Settings */}
            <button
              className="p-2.5 rounded-xl text-gallery-muted hover:text-white hover:bg-gallery-surface transition-all"
            >
              <Settings className="w-5 h-5" />
            </button>
          </motion.div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gallery-muted hover:text-white"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden py-4 border-t border-gallery-border"
          >
            {/* Mobile Search */}
            <div className="relative mb-4">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gallery-muted" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-11 pr-4 py-3 rounded-xl bg-gallery-surface border border-gallery-border text-sm"
              />
            </div>

            {/* Mobile View Options */}
            <div className="flex gap-2 mb-4">
              {viewOptions.map((option) => (
                <button
                  key={option.mode}
                  onClick={() => setViewMode(option.mode)}
                  className={cn(
                    'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm',
                    viewMode === option.mode
                      ? 'bg-orange-500/20 text-orange-400'
                      : 'bg-gallery-surface text-gallery-muted'
                  )}
                >
                  {option.icon}
                  <span>{option.label}</span>
                </button>
              ))}
            </div>

            {/* Mobile Upload */}
            <button
              onClick={() => {
                onUploadClick();
                setIsMobileMenuOpen(false);
              }}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 text-white font-medium"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Photos</span>
            </button>
          </motion.div>
        )}
      </div>
    </header>
  );
}
