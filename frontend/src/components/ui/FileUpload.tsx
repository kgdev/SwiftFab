import React, { useRef, useState } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
  accept?: string;
  maxSize?: number; // in MB
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  isUploading = false,
  accept = '.step,.stp',
  maxSize = 25
}) => {
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const validFile = files.find(file => {
      const extension = file.name.toLowerCase().split('.').pop();
      return accept.includes(extension || '');
    });
    
    if (validFile) {
      onFileSelect(validFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
      // Clear the file input value to allow re-uploading the same file
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div>
      <label 
        htmlFor="file-upload"
        className={`relative flex justify-center px-8 pt-12 pb-12 border-2 border-dashed rounded-2xl transition-all duration-300 cursor-pointer group ${
          dragOver 
            ? 'border-purple-500 bg-purple-50/50' 
            : 'border-gray-300 hover:border-purple-400 hover:bg-purple-50/30'
        }`}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
      >
        <div className="space-y-1 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <div className="flex text-sm text-gray-600">
            <span className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
              Upload a file
            </span>
            <p className="pl-1">or drag and drop</p>
          </div>
          <p className="text-xs text-gray-500">
            {accept.replace(/\./g, '').toUpperCase()} up to {maxSize}MB
          </p>
        </div>
        <input 
          id="file-upload" 
          name="file-upload" 
          type="file" 
          className="sr-only" 
          accept={accept}
          onChange={handleFileSelect}
          ref={fileInputRef}
        />
      </label>
      
      {isUploading && (
        <div className="mt-4 text-center">
          <div className="loading"></div>
          <p className="text-sm text-gray-600">Processing file...</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
