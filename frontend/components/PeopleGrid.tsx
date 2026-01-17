'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, ChevronRight, Image, Pencil, Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useGalleryStore } from '@/lib/store';
import api from '@/lib/api';
import type { Cluster } from '@/types';

interface PeopleGridProps {
  onPersonClick: (cluster: Cluster) => void;
}

export function PeopleGrid({ onPersonClick }: PeopleGridProps) {
  const { clusters, photos, updateClusterName } = useGalleryStore();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');

  const handleStartEdit = (e: React.MouseEvent, cluster: Cluster) => {
    e.stopPropagation();
    setEditingId(cluster.id);
    setEditName(cluster.name || '');
  };

  const handleSaveEdit = async (e: React.MouseEvent, clusterId: string) => {
    e.stopPropagation();
    if (editName.trim()) {
      await updateClusterName(clusterId, editName.trim());
    }
    setEditingId(null);
    setEditName('');
  };

  const handleCancelEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
    setEditName('');
  };

  const handleKeyDown = (e: React.KeyboardEvent, clusterId: string) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (editName.trim()) {
        updateClusterName(clusterId, editName.trim());
      }
      setEditingId(null);
      setEditName('');
    } else if (e.key === 'Escape') {
      setEditingId(null);
      setEditName('');
    }
  };

  if (!clusters || clusters.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center py-20"
      >
        <div className="w-20 h-20 rounded-2xl bg-gallery-surface flex items-center justify-center mb-4">
          <User className="w-10 h-10 text-gallery-muted" />
        </div>
        <h3 className="text-xl font-semibold mb-2">No people detected yet</h3>
        <p className="text-gallery-muted text-center max-w-md">
          Upload photos with faces and our AI will automatically detect and group people.
        </p>
      </motion.div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {clusters.map((cluster, index) => {
        // Find the representative photo
        const representativePhoto = photos.find(
          (p) => p.id === cluster.representative_photo_id
        );
        const thumbnailUrl = representativePhoto
          ? api.getThumbnailUrl(representativePhoto.id)
          : null;

        const isEditing = editingId === cluster.id;

        return (
          <motion.div
            key={cluster.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => !isEditing && onPersonClick(cluster)}
            className={cn(
              'group relative p-4 rounded-2xl cursor-pointer',
              'bg-gallery-surface border border-gallery-border',
              'hover:border-orange-500/30 hover:shadow-lg hover:shadow-orange-500/5',
              'transition-all duration-300 text-left'
            )}
          >
            {/* Avatar */}
            <div className="flex justify-center mb-4">
              <div className="relative">
                {thumbnailUrl ? (
                  <div className="w-24 h-24 rounded-full overflow-hidden border-2 border-gallery-border group-hover:border-orange-500/50 transition-colors">
                    <img
                      src={`${thumbnailUrl}?t=${cluster.id}`}
                      alt={cluster.name || 'Person'}
                      className="w-full h-full object-cover"
                      crossOrigin="anonymous"
                    />
                  </div>
                ) : (
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-orange-500/20 to-orange-600/20 flex items-center justify-center border-2 border-gallery-border">
                    <User className="w-10 h-10 text-orange-400" />
                  </div>
                )}
                {/* Photo count badge */}
                <div className="absolute -bottom-1 -right-1 px-2 py-0.5 rounded-full bg-orange-500 text-xs font-medium text-white">
                  {cluster.face_count}
                </div>
              </div>
            </div>

            {/* Name - Editable */}
            <div className="text-center">
              {isEditing ? (
                <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, cluster.id)}
                    placeholder="Enter name..."
                    autoFocus
                    className={cn(
                      'flex-1 px-2 py-1 rounded-lg text-sm font-semibold text-center',
                      'bg-gallery-bg border border-orange-500/50',
                      'focus:outline-none focus:border-orange-500',
                      'placeholder:text-gallery-muted'
                    )}
                  />
                  <button
                    onClick={(e) => handleSaveEdit(e, cluster.id)}
                    className="p-1 rounded-lg bg-green-500/20 hover:bg-green-500/30 text-green-400 transition-colors"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="p-1 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <h3 className="font-semibold truncate">
                    {cluster.name || `Person ${index + 1}`}
                  </h3>
                  <button
                    onClick={(e) => handleStartEdit(e, cluster)}
                    className="p-1 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-gallery-bg transition-all"
                    title="Rename"
                  >
                    <Pencil className="w-3.5 h-3.5 text-gallery-muted hover:text-orange-400" />
                  </button>
                </div>
              )}
              <p className="text-sm text-gallery-muted mt-1">
                {cluster.photo_ids?.length || 0} photos
              </p>
            </div>

            {/* Hover arrow */}
            {!isEditing && (
              <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <ChevronRight className="w-5 h-5 text-orange-400" />
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}