'use client';

import { motion } from 'framer-motion';
import { PhotoCard } from './PhotoCard';
import { useGalleryStore } from '@/lib/store';
import type { Photo, ViewMode } from '@/types';
import { cn } from '@/lib/utils';
import { ImageOff } from 'lucide-react';

interface PhotoGridProps {
  photos: Photo[];
  onPhotoClick: (photo: Photo) => void;
}

export function PhotoGrid({ photos, onPhotoClick }: PhotoGridProps) {
  const { viewMode, deletePhoto } = useGalleryStore();

  if (photos.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center py-20"
      >
        <div className="w-20 h-20 rounded-2xl bg-gallery-surface flex items-center justify-center mb-4">
          <ImageOff className="w-10 h-10 text-gallery-muted" />
        </div>
        <h3 className="text-xl font-semibold mb-2">No photos yet</h3>
        <p className="text-gallery-muted text-center max-w-md">
          Upload some photos to get started. Our AI will automatically detect
          faces, objects, and make your photos searchable.
        </p>
      </motion.div>
    );
  }

  const handleDelete = async (photo: Photo) => {
    if (confirm(`Delete "${photo.original_filename}"?`)) {
      await deletePhoto(photo.id);
    }
  };

  // Grid view
  if (viewMode === 'grid') {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
        {photos.map((photo, index) => (
          <PhotoCard
            key={photo.id}
            photo={photo}
            index={index}
            onClick={() => onPhotoClick(photo)}
            onDelete={() => handleDelete(photo)}
          />
        ))}
      </div>
    );
  }

  // Masonry view
  if (viewMode === 'masonry') {
    return (
      <div className="masonry-grid">
        {photos.map((photo, index) => (
          <div key={photo.id} className="masonry-grid-item">
            <MasonryCard
              photo={photo}
              index={index}
              onClick={() => onPhotoClick(photo)}
              onDelete={() => handleDelete(photo)}
            />
          </div>
        ))}
      </div>
    );
  }

  // Timeline view
  if (viewMode === 'timeline') {
    const groupedPhotos = groupByDate(photos);

    return (
      <div className="space-y-8">
        {Object.entries(groupedPhotos).map(([date, datePhotos]) => (
          <div key={date}>
            <div className="flex items-center gap-4 mb-4">
              <h3 className="text-lg font-semibold">{date}</h3>
              <div className="flex-1 h-px bg-gallery-border" />
              <span className="text-sm text-gallery-muted">
                {datePhotos.length} photos
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {datePhotos.map((photo, index) => (
                <PhotoCard
                  key={photo.id}
                  photo={photo}
                  index={index}
                  onClick={() => onPhotoClick(photo)}
                  onDelete={() => handleDelete(photo)}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return null;
}

// Masonry card with variable height
function MasonryCard({
  photo,
  index,
  onClick,
  onDelete,
}: {
  photo: Photo;
  index: number;
  onClick: () => void;
  onDelete: () => void;
}) {
  const aspectRatio = photo.width && photo.height 
    ? photo.width / photo.height 
    : 1;
  
  // Calculate height based on aspect ratio (for visual variety)
  const heightClass = aspectRatio > 1.3 
    ? 'h-48' 
    : aspectRatio < 0.8 
    ? 'h-80' 
    : 'h-64';

  return (
    <PhotoCard
      photo={photo}
      index={index}
      onClick={onClick}
      onDelete={onDelete}
    />
  );
}

// Group photos by date
function groupByDate(photos: Photo[]): Record<string, Photo[]> {
  return photos.reduce((groups, photo) => {
    const date = new Date(photo.upload_date).toLocaleDateString('en-GB', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(photo);
    return groups;
  }, {} as Record<string, Photo[]>);
}
