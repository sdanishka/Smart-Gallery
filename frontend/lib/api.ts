import type { Photo, Cluster, Category, GalleryStats, SearchResult } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

const api = {
  // Photos
  async getPhotos(): Promise<Photo[]> {
    return request<Photo[]>('/photos');
  },

  async uploadPhoto(file: File): Promise<Photo> {
    const formData = new FormData();
    formData.append('file', file);
    return request<Photo>('/photos/upload', {
      method: 'POST',
      body: formData,
    });
  },

  async uploadPhotos(files: File[]): Promise<Photo[]> {
    const results: Photo[] = [];
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      const photo = await request<Photo>('/photos/upload', {
        method: 'POST',
        body: formData,
      });
      results.push(photo);
    }
    return results;
  },

  async deletePhoto(photoId: string): Promise<void> {
    await request(`/photos/${photoId}`, { method: 'DELETE' });
  },

  getImageUrl(photoId: string): string {
    return `${API_BASE}/photos/${photoId}/image`;
  },

  getThumbnailUrl(photoId: string): string {
    return `${API_BASE}/photos/${photoId}/thumbnail`;
  },

  // Clusters (People)
  async getClusters(): Promise<Cluster[]> {
    return request<Cluster[]>('/clusters');
  },

  async updateCluster(clusterId: string, name: string): Promise<Cluster> {
    return request<Cluster>(`/clusters/${clusterId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    });
  },

  // Categories
  async getCategories(): Promise<Category[]> {
    return request<Category[]>('/categories');
  },

  // Stats
  async getStats(): Promise<GalleryStats> {
    return request<GalleryStats>('/stats');
  },

  // Search
  async search(query: string): Promise<SearchResult[]> {
    return request<SearchResult[]>(`/search?q=${encodeURIComponent(query)}`);
  },
};

export default api;