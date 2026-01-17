// Photo and AI detection types

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_name: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface Face {
  id: string;
  bbox: BoundingBox;
  confidence: number;
  age?: number;
  gender?: string;
  cluster_id?: string;
  embedding?: number[];
}

export interface Photo {
  id: string;
  filename: string;
  original_filename: string;
  upload_date: string;
  width: number;
  height: number;
  file_size: number;
  mime_type: string;
  detections: Detection[];
  faces: Face[];
  clip_embedding?: number[];
  thumbnail_url: string;
  image_url: string;
}

export interface Cluster {
  id: string;
  name?: string;
  face_count: number;
  representative_photo_id: string;
  photo_ids: string[];
}

export interface Category {
  name: string;
  count: number;
  photo_ids: string[];
}

export interface GalleryStats {
  total_photos: number;
  total_faces: number;
  total_people: number;
  total_objects: number;
  categories: { [key: string]: number };
  storage_used: number;
}

export interface UploadProgress {
  filename: string;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
}

export interface SearchResult {
  photo: Photo;
  similarity: number;
  match_type: 'face' | 'object' | 'semantic';
}

export type ViewMode = 'grid' | 'masonry' | 'timeline';
export type SortOrder = 'date_desc' | 'date_asc' | 'name' | 'size';
export type FilterType = 'all' | 'people' | 'objects' | 'category';
