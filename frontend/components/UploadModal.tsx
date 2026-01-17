'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Upload,
  Image,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
} from 'lucide-react';
import { cn, formatBytes } from '@/lib/utils';
import { useGalleryStore } from '@/lib/store';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const [files, setFiles] = useState<File[]>([]);
  const { uploadPhotos, isUploading, uploadProgress } = useGalleryStore();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const handleUpload = async () => {
    if (files.length === 0) return;
    await uploadPhotos(files);
    setFiles([]);
    onClose();
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const totalSize = files.reduce((sum, f) => sum + f.size, 0);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/80 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="relative w-full max-w-2xl max-h-[90vh] flex flex-col bg-gallery-surface rounded-2xl border border-gallery-border shadow-2xl overflow-hidden"
        >
          {/* Header */}
          <div className="flex-shrink-0 flex items-center justify-between p-6 border-b border-gallery-border">
            <div>
              <h2 className="text-xl font-bold">Upload Photos</h2>
              <p className="text-sm text-gallery-muted mt-1">
                Drag and drop or select files to upload
              </p>
            </div>
            <button
              onClick={onClose}
              disabled={isUploading}
              className="p-2 rounded-lg hover:bg-gallery-bg transition-colors disabled:opacity-50"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content - scrollable */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={cn(
                'relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer',
                'transition-all duration-300',
                isDragActive
                  ? 'border-orange-500 bg-orange-500/10'
                  : 'border-gallery-border hover:border-orange-500/50 hover:bg-gallery-bg',
                isUploading && 'pointer-events-none opacity-50'
              )}
            >
              <input {...getInputProps()} />
              <div className="flex flex-col items-center gap-4">
                <div
                  className={cn(
                    'w-16 h-16 rounded-2xl flex items-center justify-center',
                    'transition-colors',
                    isDragActive
                      ? 'bg-orange-500/20'
                      : 'bg-gallery-bg'
                  )}
                >
                  <Upload
                    className={cn(
                      'w-8 h-8 transition-colors',
                      isDragActive ? 'text-orange-400' : 'text-gallery-muted'
                    )}
                  />
                </div>
                <div>
                  <p className="text-lg font-medium">
                    {isDragActive
                      ? 'Drop your photos here'
                      : 'Drag photos here or click to browse'}
                  </p>
                  <p className="text-sm text-gallery-muted mt-1">
                    Supports PNG, JPG, GIF, WebP, HEIC up to 50MB
                  </p>
                </div>
              </div>

              {/* Processing info */}
              <div className="absolute bottom-4 left-4 right-4">
                <div className="flex items-center justify-center gap-6 text-xs text-gallery-muted">
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-orange-400" />
                    Face Detection
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-orange-400" />
                    Object Recognition
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-orange-400" />
                    Semantic Search
                  </span>
                </div>
              </div>
            </div>

            {/* File list */}
            {files.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium">
                    {files.length} file{files.length !== 1 && 's'} selected
                  </h3>
                  <span className="text-sm text-gallery-muted">
                    {formatBytes(totalSize)}
                  </span>
                </div>

                <div className="max-h-60 overflow-y-auto space-y-2">
                  {files.map((file, index) => {
                    const progress = uploadProgress.find(
                      (p) => p.filename === file.name
                    );

                    return (
                      <motion.div
                        key={`${file.name}-${index}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center gap-3 p-3 rounded-lg bg-gallery-bg"
                      >
                        {/* Preview */}
                        <div className="w-12 h-12 rounded-lg overflow-hidden bg-gallery-elevated flex-shrink-0">
                          <img
                            src={URL.createObjectURL(file)}
                            alt={file.name}
                            className="w-full h-full object-cover"
                          />
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {file.name}
                          </p>
                          <p className="text-xs text-gallery-muted">
                            {formatBytes(file.size)}
                          </p>

                          {/* Progress bar */}
                          {progress && (
                            <div className="mt-2">
                              <div className="h-1 rounded-full bg-gallery-border overflow-hidden">
                                <motion.div
                                  className={cn(
                                    'h-full rounded-full',
                                    progress.status === 'error'
                                      ? 'bg-red-500'
                                      : progress.status === 'complete'
                                        ? 'bg-green-500'
                                        : 'bg-orange-500'
                                  )}
                                  initial={{ width: 0 }}
                                  animate={{
                                    width: `${progress.progress}%`,
                                  }}
                                />
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Status / Remove */}
                        {progress ? (
                          <div className="flex-shrink-0">
                            {progress.status === 'complete' && (
                              <CheckCircle2 className="w-5 h-5 text-green-500" />
                            )}
                            {progress.status === 'error' && (
                              <AlertCircle className="w-5 h-5 text-red-500" />
                            )}
                            {(progress.status === 'uploading' ||
                              progress.status === 'processing') && (
                                <Loader2 className="w-5 h-5 text-orange-400 animate-spin" />
                              )}
                          </div>
                        ) : (
                          <button
                            onClick={() => removeFile(index)}
                            className="p-1.5 rounded-lg hover:bg-gallery-surface transition-colors text-gallery-muted hover:text-white"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Footer - always visible at bottom */}
          <div className="flex-shrink-0 flex items-center justify-between p-6 border-t border-gallery-border bg-gallery-bg/50">
            <button
              onClick={() => setFiles([])}
              disabled={isUploading || files.length === 0}
              className="px-4 py-2 rounded-lg text-sm text-gallery-muted hover:text-white hover:bg-gallery-surface transition-all disabled:opacity-50"
            >
              Clear all
            </button>
            <button
              onClick={handleUpload}
              disabled={isUploading || files.length === 0}
              className={cn(
                'flex items-center gap-2 px-6 py-2.5 rounded-xl',
                'bg-gradient-to-r from-orange-500 to-orange-600',
                'text-white font-medium text-sm',
                'hover:from-orange-600 hover:to-orange-700',
                'transition-all duration-300',
                'shadow-lg shadow-orange-500/25',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>
                    Upload {files.length} photo{files.length !== 1 && 's'}
                  </span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}