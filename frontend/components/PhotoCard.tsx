'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Heart,
  Download,
  Trash2,
  Share2,
  Eye,
  User,
  Tag,
  MoreHorizontal,
} from 'lucide-react';
import { cn, formatDate, capitalizeFirst, getConfidenceBg } from '@/lib/utils';
import api from '@/lib/api';
import type { Photo } from '@/types';

interface PhotoCardProps {
  photo: Photo;
  index: number;
  onClick: () => void;
  onDelete: () => void;
}

export function PhotoCard({ photo, index, onClick, onDelete }: PhotoCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const thumbnailUrl = api.getThumbnailUrl(photo.id);
  const imageUrl = api.getImageUrl(photo.id);

  const topDetections = photo.detections?.slice(0, 3) || [];
  const faceCount = photo.faces?.length || 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.03, duration: 0.3 }}
      className="group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowMenu(false);
      }}
    >
      <div
        onClick={onClick}
        className={cn(
          'relative aspect-square rounded-2xl overflow-hidden cursor-pointer',
          'bg-gallery-surface border border-gallery-border',
          'transition-all duration-300',
          'hover:border-orange-500/30 hover:shadow-xl hover:shadow-orange-500/5',
          isHovered && 'scale-[1.02]'
        )}
      >
        {/* Loading shimmer */}
        {!isImageLoaded && (
          <div className="absolute inset-0 shimmer" />
        )}

        {/* Image */}
        <img
          src={`${thumbnailUrl}?t=${photo.id}`}
          alt={photo.original_filename}
          className={cn(
            'w-full h-full object-cover transition-all duration-500',
            isImageLoaded ? 'opacity-100' : 'opacity-0',
            isHovered && 'scale-105'
          )}
          onLoad={() => setIsImageLoaded(true)}
          crossOrigin="anonymous"
        />

        {/* Gradient overlay */}
        <div
          className={cn(
            'absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent',
            'opacity-0 group-hover:opacity-100 transition-opacity duration-300'
          )}
        />

        {/* Face count badge */}
        {faceCount > 0 && (
          <div className="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-sm text-xs font-medium">
            <User className="w-3 h-3 text-orange-400" />
            <span>{faceCount}</span>
          </div>
        )}

        {/* Detection badges */}
        {topDetections.length > 0 && (
          <div className="absolute top-3 right-3 flex flex-wrap gap-1.5 justify-end max-w-[60%]">
            {topDetections.map((det, i) => (
              <span
                key={i}
                className={cn(
                  'px-2 py-0.5 rounded-full text-[10px] font-medium backdrop-blur-sm',
                  'bg-black/60 text-white'
                )}
              >
                {capitalizeFirst(det.class_name)}
              </span>
            ))}
          </div>
        )}

        {/* Bottom info - visible on hover */}
        <div
          className={cn(
            'absolute bottom-0 left-0 right-0 p-4',
            'translate-y-full group-hover:translate-y-0 transition-transform duration-300'
          )}
        >
          <p className="text-sm font-medium truncate">
            {photo.original_filename}
          </p>
          <p className="text-xs text-gallery-muted mt-1">
            {formatDate(photo.upload_date)}
          </p>
        </div>

        {/* Quick actions - visible on hover */}
        <div
          className={cn(
            'absolute top-3 right-3',
            'opacity-0 group-hover:opacity-100 transition-opacity duration-300',
            topDetections.length > 0 && 'top-12'
          )}
        >
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="p-2 rounded-full bg-black/60 backdrop-blur-sm hover:bg-black/80 transition-colors"
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>

            {/* Dropdown menu */}
            {showMenu && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute top-full right-0 mt-2 w-40 py-2 rounded-xl bg-gallery-elevated border border-gallery-border shadow-xl z-10"
              >
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onClick();
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gallery-muted hover:text-white hover:bg-gallery-surface transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  View
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    window.open(imageUrl, '_blank');
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gallery-muted hover:text-white hover:bg-gallery-surface transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gallery-muted hover:text-white hover:bg-gallery-surface transition-colors"
                >
                  <Heart className="w-4 h-4" />
                  Favorite
                </button>
                <hr className="my-2 border-gallery-border" />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
