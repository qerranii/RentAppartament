'use client';

import { useCallback } from 'react';
import toast from 'react-hot-toast';

interface ImageUploadProps {
  onUpload: (files: File[]) => void;
  maxFiles?: number;
}

export default function ImageUpload({ onUpload, maxFiles = 5 }: ImageUploadProps) {
  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const files = Array.from(e.dataTransfer.files).filter((f) =>
        ['image/jpeg', 'image/png', 'image/webp'].includes(f.type)
      );

      if (files.length > maxFiles) {
        toast.error(`Maximum ${maxFiles} files allowed`);
        return;
      }

      onUpload(files);
    },
    [maxFiles, onUpload]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > maxFiles) {
      toast.error(`Maximum ${maxFiles} files allowed`);
      return;
    }
    onUpload(files);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center hover:border-blue-500 transition cursor-pointer bg-blue-50"
    >
      <input
        type="file"
        multiple
        accept="image/*"
        onChange={handleChange}
        className="hidden"
        id="image-upload"
      />
      <label htmlFor="image-upload" className="cursor-pointer block">
        <p className="text-lg font-semibold text-gray-800">
          📸 Drag & drop images here
        </p>
        <p className="text-sm text-gray-600">or click to select files</p>
        <p className="text-xs text-gray-500 mt-2">
          Supported: JPG, PNG, WebP (max {maxFiles} files)
        </p>
      </label>
    </div>
  );
}
