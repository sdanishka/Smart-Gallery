import { create } from 'zustand';
import type { Photo, Cluster, Category, GalleryStats, ViewMode, SortOrder, UploadProgress } from '@/types';
import api from './api';

interface GalleryState {
  // Data
  photos: Photo[];
  clusters: Cluster[];
  categories: Category[];
  stats: GalleryStats | null;

  // UI State
  viewMode: ViewMode;
  sortOrder: SortOrder;
  selectedPhoto: Photo | null;
  selectedCluster: Cluster | null;
  selectedCategory: Category | null;
  searchQuery: string;
  isUploading: boolean;
  uploadProgress: UploadProgress[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setViewMode: (mode: ViewMode) => void;
  setSortOrder: (order: SortOrder) => void;
  setSelectedPhoto: (photo: Photo | null) => void;
  setSelectedCluster: (cluster: Cluster | null) => void;
  setSelectedCategory: (category: Category | null) => void;
  setSearchQuery: (query: string) => void;

  // API Actions
  fetchPhotos: () => Promise<void>;
  fetchClusters: () => Promise<void>;
  fetchCategories: () => Promise<void>;
  fetchStats: () => Promise<void>;
  fetchAll: () => Promise<void>;
  uploadPhotos: (files: File[]) => Promise<void>;
  deletePhoto: (id: string) => Promise<void>;
  updateClusterName: (clusterId: string, name: string) => Promise<void>;
}

export const useGalleryStore = create<GalleryState>((set, get) => ({
  // Initial Data
  photos: [],
  clusters: [],
  categories: [],
  stats: null,

  // Initial UI State
  viewMode: 'grid',
  sortOrder: 'date_desc',
  selectedPhoto: null,
  selectedCluster: null,
  selectedCategory: null,
  searchQuery: '',
  isUploading: false,
  uploadProgress: [],
  isLoading: false,
  error: null,

  // UI Actions
  setViewMode: (mode) => set({ viewMode: mode }),
  setSortOrder: (order) => set({ sortOrder: order }),
  setSelectedPhoto: (photo) => set({ selectedPhoto: photo }),
  setSelectedCluster: (cluster) => set({ selectedCluster: cluster }),
  setSelectedCategory: (category) => set({ selectedCategory: category }),
  setSearchQuery: (query) => set({ searchQuery: query }),

  // API Actions
  fetchPhotos: async () => {
    try {
      const photos = await api.getPhotos();
      set({ photos, error: null });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  fetchClusters: async () => {
    try {
      const clusters = await api.getClusters();
      set({ clusters, error: null });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  fetchCategories: async () => {
    try {
      const categories = await api.getCategories();
      set({ categories, error: null });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  fetchStats: async () => {
    try {
      const stats = await api.getStats();
      set({ stats, error: null });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  fetchAll: async () => {
    set({ isLoading: true });
    try {
      await Promise.all([
        get().fetchPhotos(),
        get().fetchClusters(),
        get().fetchCategories(),
        get().fetchStats(),
      ]);
    } finally {
      set({ isLoading: false });
    }
  },

  uploadPhotos: async (files) => {
    set({ isUploading: true });

    const progress: UploadProgress[] = files.map((f) => ({
      filename: f.name,
      progress: 0,
      status: 'pending',
    }));
    set({ uploadProgress: progress });

    try {
      // Update to uploading status
      set({
        uploadProgress: progress.map((p) => ({ ...p, status: 'uploading', progress: 50 })),
      });

      const newPhotos = await api.uploadPhotos(files);

      // Update to complete
      set({
        uploadProgress: progress.map((p) => ({ ...p, status: 'complete', progress: 100 })),
      });

      // Refresh data
      await get().fetchAll();

      // Clear upload progress after delay
      setTimeout(() => {
        set({ uploadProgress: [], isUploading: false });
      }, 2000);
    } catch (error) {
      set({
        uploadProgress: progress.map((p) => ({
          ...p,
          status: 'error',
          error: (error as Error).message,
        })),
        isUploading: false,
      });
    }
  },

  deletePhoto: async (id) => {
    try {
      await api.deletePhoto(id);
      set({ photos: get().photos.filter((p) => p.id !== id) });
      await get().fetchStats();
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  updateClusterName: async (clusterId: string, name: string) => {
    try {
      const updatedCluster = await api.updateCluster(clusterId, name);

      // Update the cluster in state
      set((state) => ({
        clusters: state.clusters.map((c) =>
          c.id === clusterId ? { ...c, name: updatedCluster.name } : c
        ),
      }));
    } catch (error) {
      console.error('Failed to update cluster name:', error);
      set({ error: (error as Error).message });
    }
  },
}));