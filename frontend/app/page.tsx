'use client';

import { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import {
  Header,
  Sidebar,
  PhotoGrid,
  PhotoViewer,
  UploadModal,
  StatsCards,
  PeopleGrid,
  CategoriesGrid,
  LoadingState,
} from '@/components';
import { useGalleryStore } from '@/lib/store';
import type { Photo, Cluster, Category } from '@/types';

export default function GalleryPage() {
  const [activeSection, setActiveSection] = useState('all');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);
  
  const {
    photos,
    clusters,
    categories,
    isLoading,
    error,
    searchQuery,
    sortOrder,
    fetchAll,
    deletePhoto,
    setSelectedCluster,
    setSelectedCategory,
  } = useGalleryStore();

  // Fetch data on mount
  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  // Show error toast
  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  // Filter and sort photos
  const filteredPhotos = useMemo(() => {
    let result = [...photos];

    // Filter by section
    if (activeSection === 'people') {
      // Show photos with faces
      result = result.filter((p) => p.faces && p.faces.length > 0);
    } else if (activeSection === 'objects') {
      // Show photos with detections
      result = result.filter((p) => p.detections && p.detections.length > 0);
    } else if (activeSection === 'favorites') {
      // TODO: Implement favorites
      result = [];
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter((photo) => {
        // Search in filename
        if (photo.original_filename.toLowerCase().includes(query)) return true;
        
        // Search in detections
        if (photo.detections?.some((d) => 
          d.class_name.toLowerCase().includes(query)
        )) return true;
        
        return false;
      });
    }

    // Sort
    switch (sortOrder) {
      case 'date_desc':
        result.sort((a, b) => 
          new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()
        );
        break;
      case 'date_asc':
        result.sort((a, b) => 
          new Date(a.upload_date).getTime() - new Date(b.upload_date).getTime()
        );
        break;
      case 'name':
        result.sort((a, b) => 
          a.original_filename.localeCompare(b.original_filename)
        );
        break;
      case 'size':
        result.sort((a, b) => b.file_size - a.file_size);
        break;
    }

    return result;
  }, [photos, activeSection, searchQuery, sortOrder]);

  // Handle person click
  const handlePersonClick = (cluster: Cluster) => {
    setSelectedCluster(cluster);
    // Filter to show only photos containing this person
    // For now, just switch to all and show a toast
    toast.info(`Showing photos of ${cluster.name || 'this person'}`);
  };

  // Handle category click
  const handleCategoryClick = (category: Category) => {
    setSelectedCategory(category);
    toast.info(`Showing photos with ${category.name}`);
  };

  // Handle photo delete
  const handleDeletePhoto = async (photo: Photo) => {
    await deletePhoto(photo.id);
    toast.success('Photo deleted');
  };

  // Section titles
  const sectionTitles: Record<string, string> = {
    all: 'All Photos',
    people: 'People',
    objects: 'Objects',
    favorites: 'Favorites',
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <Header onUploadClick={() => setIsUploadOpen(true)} />

      {/* Main content */}
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-8">
          {/* Sidebar */}
          <Sidebar
            activeSection={activeSection}
            onSectionChange={setActiveSection}
          />

          {/* Main area */}
          <main className="flex-1 min-w-0">
            {isLoading ? (
              <LoadingState />
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-8"
              >
                {/* Stats - only show on All Photos */}
                {activeSection === 'all' && <StatsCards />}

                {/* Section header */}
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">
                      {sectionTitles[activeSection]}
                    </h2>
                    <p className="text-gallery-muted mt-1">
                      {activeSection === 'all' && `${filteredPhotos.length} photos`}
                      {activeSection === 'people' && `${clusters?.length || 0} people detected`}
                      {activeSection === 'objects' && `${categories?.length || 0} categories`}
                      {activeSection === 'favorites' && 'Your favorite photos'}
                    </p>
                  </div>

                  {/* Sort dropdown - only for photo views */}
                  {(activeSection === 'all' || activeSection === 'favorites') && (
                    <select
                      value={sortOrder}
                      onChange={(e) => useGalleryStore.getState().setSortOrder(e.target.value as any)}
                      className="px-4 py-2 rounded-lg bg-gallery-surface border border-gallery-border text-sm focus:outline-none focus:border-orange-500/50"
                    >
                      <option value="date_desc">Newest first</option>
                      <option value="date_asc">Oldest first</option>
                      <option value="name">Name</option>
                      <option value="size">Size</option>
                    </select>
                  )}
                </div>

                {/* Content based on section */}
                <AnimatePresence mode="wait">
                  {activeSection === 'all' && (
                    <motion.div
                      key="all"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <PhotoGrid
                        photos={filteredPhotos}
                        onPhotoClick={setSelectedPhoto}
                      />
                    </motion.div>
                  )}

                  {activeSection === 'people' && (
                    <motion.div
                      key="people"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <PeopleGrid onPersonClick={handlePersonClick} />
                    </motion.div>
                  )}

                  {activeSection === 'objects' && (
                    <motion.div
                      key="objects"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <CategoriesGrid onCategoryClick={handleCategoryClick} />
                    </motion.div>
                  )}

                  {activeSection === 'favorites' && (
                    <motion.div
                      key="favorites"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="flex flex-col items-center justify-center py-20"
                    >
                      <div className="w-20 h-20 rounded-2xl bg-gallery-surface flex items-center justify-center mb-4">
                        <span className="text-4xl">⭐</span>
                      </div>
                      <h3 className="text-xl font-semibold mb-2">No favorites yet</h3>
                      <p className="text-gallery-muted text-center max-w-md">
                        Click the heart icon on any photo to add it to your favorites.
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}
          </main>
        </div>
      </div>

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
      />

      {/* Photo Viewer */}
      <PhotoViewer
        photo={selectedPhoto}
        photos={filteredPhotos}
        onClose={() => setSelectedPhoto(null)}
        onNavigate={setSelectedPhoto}
        onDelete={handleDeletePhoto}
      />
    </div>
  );
}
