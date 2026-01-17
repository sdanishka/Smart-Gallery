'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  ChevronLeft,
  ChevronRight,
  Download,
  Trash2,
  Heart,
  Share2,
  Info,
  User,
  Tag,
  ZoomIn,
  ZoomOut,
  Maximize2,
} from 'lucide-react';
import { cn, formatDate, formatBytes, capitalizeFirst, getConfidenceBg } from '@/lib/utils';
import api from '@/lib/api';
import type { Photo } from '@/types';

interface PhotoViewerProps {
  photo: Photo | null;
  photos: Photo[];
  onClose: () => void;
  onNavigate: (photo: Photo) => void;
  onDelete: (photo: Photo) => void;
}

export function PhotoViewer({
  photo,
  photos,
  onClose,
  onNavigate,
  onDelete,
}: PhotoViewerProps) {
  const [showInfo, setShowInfo] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const currentIndex = photos.findIndex((p) => p.id === photo?.id);
  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex < photos.length - 1;

  const handlePrev = useCallback(() => {
    if (hasPrev) {
      onNavigate(photos[currentIndex - 1]);
      setIsLoading(true);
      setZoom(1);
    }
  }, [currentIndex, hasPrev, onNavigate, photos]);

  const handleNext = useCallback(() => {
    if (hasNext) {
      onNavigate(photos[currentIndex + 1]);
      setIsLoading(true);
      setZoom(1);
    }
  }, [currentIndex, hasNext, onNavigate, photos]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') handlePrev();
      if (e.key === 'ArrowRight') handleNext();
      if (e.key === 'i') setShowInfo((v) => !v);
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleNext, handlePrev, onClose]);

  if (!photo) return null;

  const imageUrl = api.getImageUrl(photo.id);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex"
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/95 backdrop-blur-xl"
          onClick={onClose}
        />

        {/* Main content */}
        <div className="relative flex-1 flex">
          {/* Navigation - Left */}
          <button
            onClick={handlePrev}
            disabled={!hasPrev}
            className={cn(
              'absolute left-4 top-1/2 -translate-y-1/2 z-10',
              'p-3 rounded-full bg-white/10 backdrop-blur-sm',
              'hover:bg-white/20 transition-all',
              'disabled:opacity-30 disabled:cursor-not-allowed'
            )}
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          {/* Navigation - Right */}
          <button
            onClick={handleNext}
            disabled={!hasNext}
            className={cn(
              'absolute right-4 top-1/2 -translate-y-1/2 z-10',
              showInfo && 'right-[340px]',
              'p-3 rounded-full bg-white/10 backdrop-blur-sm',
              'hover:bg-white/20 transition-all',
              'disabled:opacity-30 disabled:cursor-not-allowed'
            )}
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          {/* Image container */}
          <div
            className={cn(
              'flex-1 flex items-center justify-center p-8',
              showInfo && 'pr-[340px]'
            )}
          >
            <motion.div
              key={photo.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative max-w-full max-h-full"
            >
              {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
              <img
                src={`${imageUrl}?t=${photo.id}`}
                alt={photo.original_filename}
                className={cn(
                  'max-w-full max-h-[85vh] object-contain rounded-lg',
                  'transition-all duration-300',
                  isLoading && 'opacity-0'
                )}
                style={{ transform: `scale(${zoom})` }}
                onLoad={() => setIsLoading(false)}
                crossOrigin="anonymous"
              />
            </motion.div>
          </div>

          {/* Top bar */}
          <div className="absolute top-0 left-0 right-0 p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gallery-muted">
                {currentIndex + 1} / {photos.length}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {/* Zoom controls */}
              <button
                onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                title="Zoom out"
              >
                <ZoomOut className="w-5 h-5" />
              </button>
              <span className="text-sm w-16 text-center">
                {Math.round(zoom * 100)}%
              </span>
              <button
                onClick={() => setZoom((z) => Math.min(3, z + 0.25))}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                title="Zoom in"
              >
                <ZoomIn className="w-5 h-5" />
              </button>

              <div className="w-px h-6 bg-white/20 mx-2" />

              {/* Actions */}
              <button
                onClick={() => window.open(imageUrl, '_blank')}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                title="Download"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                title="Favorite"
              >
                <Heart className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowInfo(!showInfo)}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  showInfo
                    ? 'bg-orange-500/20 text-orange-400'
                    : 'bg-white/10 hover:bg-white/20'
                )}
                title="Toggle info"
              >
                <Info className="w-5 h-5" />
              </button>
              <button
                onClick={() => {
                  if (confirm('Delete this photo?')) {
                    onDelete(photo);
                    onClose();
                  }
                }}
                className="p-2 rounded-lg bg-white/10 hover:bg-red-500/20 hover:text-red-400 transition-colors"
                title="Delete"
              >
                <Trash2 className="w-5 h-5" />
              </button>

              <div className="w-px h-6 bg-white/20 mx-2" />

              <button
                onClick={onClose}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                title="Close (Esc)"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Info panel */}
          <AnimatePresence>
            {showInfo && (
              <motion.div
                initial={{ x: 320, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 320, opacity: 0 }}
                className="absolute top-0 right-0 bottom-0 w-[320px] bg-gallery-surface border-l border-gallery-border overflow-y-auto"
              >
                <div className="p-6 space-y-6">
                  {/* Filename */}
                  <div>
                    <h2 className="font-semibold text-lg mb-1 truncate">
                      {photo.original_filename}
                    </h2>
                    <p className="text-sm text-gallery-muted">
                      {formatDate(photo.upload_date)}
                    </p>
                  </div>

                  {/* Details */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-gallery-muted uppercase tracking-wider">
                      Details
                    </h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-gallery-muted">Dimensions</p>
                        <p>
                          {photo.width} × {photo.height}
                        </p>
                      </div>
                      <div>
                        <p className="text-gallery-muted">Size</p>
                        <p>{formatBytes(photo.file_size)}</p>
                      </div>
                      <div>
                        <p className="text-gallery-muted">Type</p>
                        <p>{photo.mime_type}</p>
                      </div>
                    </div>
                  </div>

                  {/* Faces */}
                  {photo.faces && photo.faces.length > 0 && (
                    <div className="space-y-3">
                      <h3 className="text-sm font-semibold text-gallery-muted uppercase tracking-wider flex items-center gap-2">
                        <User className="w-4 h-4" />
                        People ({photo.faces.length})
                      </h3>
                      <div className="space-y-2">
                        {photo.faces.map((face, i) => (
                          <div
                            key={face.id || i}
                            className="flex items-center gap-3 p-2 rounded-lg bg-gallery-bg"
                          >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500/20 to-orange-600/20 flex items-center justify-center">
                              <User className="w-5 h-5 text-orange-400" />
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-medium">
                                Person {i + 1}
                              </p>
                              <div className="flex items-center gap-2 text-xs text-gallery-muted">
                                {face.age && <span>{face.age} yrs</span>}
                                {face.gender && (
                                  <span>{capitalizeFirst(face.gender)}</span>
                                )}
                                <span>
                                  {(face.confidence * 100).toFixed(0)}% conf
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Objects */}
                  {photo.detections && photo.detections.length > 0 && (
                    <div className="space-y-3">
                      <h3 className="text-sm font-semibold text-gallery-muted uppercase tracking-wider flex items-center gap-2">
                        <Tag className="w-4 h-4" />
                        Objects ({photo.detections.length})
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {photo.detections.map((det, i) => (
                          <span
                            key={i}
                            className={cn(
                              'px-3 py-1.5 rounded-full text-xs font-medium',
                              'border',
                              getConfidenceBg(det.confidence)
                            )}
                          >
                            {capitalizeFirst(det.class_name)}
                            <span className="ml-1.5 opacity-60">
                              {(det.confidence * 100).toFixed(0)}%
                            </span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* CLIP Embedding Info */}
                  {photo.clip_embedding && (
                    <div className="space-y-3">
                      <h3 className="text-sm font-semibold text-gallery-muted uppercase tracking-wider">
                        AI Features
                      </h3>
                      <div className="p-3 rounded-lg bg-gradient-to-br from-orange-500/10 to-orange-600/5 border border-orange-500/20">
                        <p className="text-sm">
                          <span className="text-orange-400">✓</span> CLIP
                          embedding generated
                        </p>
                        <p className="text-xs text-gallery-muted mt-1">
                          This photo can be found via semantic search
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
