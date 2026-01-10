"use client";

import React, { useState, useRef } from 'react';

interface UploadAreaProps {
    onUpload: (file: File) => void;
    isProcessing: boolean;
}

export default function UploadArea({ onUpload, isProcessing }: UploadAreaProps) {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onUpload(e.dataTransfer.files[0]);
        }
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            onUpload(e.target.files[0]);
        }
    };

    return (
        <div
            className={`relative w-full h-64 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group
        ${isDragging ? 'border-primary bg-primary/10' : 'border-slate-700 hover:border-slate-500 hover:bg-slate-800/50'}
        ${isProcessing ? 'pointer-events-none opacity-50' : ''}
      `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
        >
            <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="image/*,.csv,.json"
            />

            <div className="bg-slate-800 p-4 rounded-full mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-black/20">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
            </div>

            <p className="text-lg font-medium text-slate-200">
                {isProcessing ? "Processing..." : "Drop report or image here"}
            </p>
            <p className="text-sm text-slate-400 mt-2">
                Supports: Histopathology, Ultrasound, CT/MRI, CSV Reports
            </p>
        </div>
    );
}
