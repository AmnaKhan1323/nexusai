"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileUp, CheckCircle, XCircle, File } from "lucide-react";
import { uploadDocument } from "@/lib/api";
import Spinner from "./ui/Spinner";

interface DocumentUploadProps {
  onUploadComplete: () => void;
}

interface UploadState {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  message: string;
}

export default function DocumentUpload({
  onUploadComplete,
}: DocumentUploadProps) {
  const [uploads, setUploads] = useState<UploadState[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const newUploads: UploadState[] = acceptedFiles.map((file) => ({
        file,
        progress: 0,
        status: "pending" as const,
        message: "Waiting to upload...",
      }));

      setUploads((prev) => [...prev, ...newUploads]);

      for (let i = 0; i < acceptedFiles.length; i++) {
        const file = acceptedFiles[i];
        const uploadIdx = uploads.length + i;

        setUploads((prev) =>
          prev.map((u, idx) =>
            idx === uploadIdx
              ? { ...u, status: "uploading", progress: 30, message: "Uploading..." }
              : u
          )
        );

        try {
          setUploads((prev) =>
            prev.map((u, idx) =>
              idx === uploadIdx
                ? { ...u, progress: 60, message: "Processing document..." }
                : u
            )
          );

          const result = await uploadDocument(file);

          setUploads((prev) =>
            prev.map((u, idx) =>
              idx === uploadIdx
                ? {
                    ...u,
                    status: "success",
                    progress: 100,
                    message: result.message || "Upload complete!",
                  }
                : u
            )
          );
        } catch (error: any) {
          setUploads((prev) =>
            prev.map((u, idx) =>
              idx === uploadIdx
                ? {
                    ...u,
                    status: "error",
                    progress: 0,
                    message:
                      error?.response?.data?.detail || "Upload failed. Please try again.",
                  }
                : u
            )
          );
        }
      }

      onUploadComplete();
    },
    [uploads.length, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxSize: 50 * 1024 * 1024,
    multiple: true,
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-300 ${
          isDragActive
            ? "border-brand-500 bg-brand-500/10"
            : "border-gray-700 bg-surface-800/30 hover:border-gray-600 hover:bg-surface-800/50"
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center">
          <div
            className={`mb-4 rounded-2xl p-4 ${
              isDragActive
                ? "bg-brand-500/20 text-brand-400"
                : "bg-surface-700/50 text-gray-400"
            }`}
          >
            <Upload className="h-10 w-10" />
          </div>
          {isDragActive ? (
            <p className="text-lg font-medium text-brand-400">
              Drop your files here...
            </p>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-300">
                Drag & drop files here, or click to browse
              </p>
              <p className="mt-2 text-sm text-gray-500">
                Supports PDF and DOCX files up to 50MB
              </p>
            </>
          )}
        </div>
      </div>

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <div className="space-y-3">
          {uploads.map((upload, idx) => (
            <div
              key={idx}
              className="flex items-center gap-4 rounded-xl border border-gray-800 bg-surface-800/30 px-4 py-3"
            >
              <div
                className={`rounded-lg p-2 ${
                  upload.status === "success"
                    ? "bg-emerald-500/20 text-emerald-400"
                    : upload.status === "error"
                      ? "bg-red-500/20 text-red-400"
                      : "bg-brand-500/20 text-brand-400"
                }`}
              >
                {upload.status === "success" ? (
                  <CheckCircle className="h-5 w-5" />
                ) : upload.status === "error" ? (
                  <XCircle className="h-5 w-5" />
                ) : upload.status === "uploading" ? (
                  <Spinner size="sm" />
                ) : (
                  <FileUp className="h-5 w-5" />
                )}
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <p className="truncate text-sm font-medium text-gray-300">
                    {upload.file.name}
                  </p>
                  <span className="ml-2 flex-shrink-0 text-xs text-gray-500">
                    {formatFileSize(upload.file.size)}
                  </span>
                </div>
                <p
                  className={`mt-0.5 text-xs ${
                    upload.status === "error" ? "text-red-400" : "text-gray-500"
                  }`}
                >
                  {upload.message}
                </p>
                {upload.status === "uploading" && (
                  <div className="mt-2 h-1 overflow-hidden rounded-full bg-surface-700">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-brand-500 to-violet-500 transition-all duration-500"
                      style={{ width: `${upload.progress}%` }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
