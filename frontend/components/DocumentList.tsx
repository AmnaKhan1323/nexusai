"use client";

import { FileText, Trash2, Clock, Hash, HardDrive } from "lucide-react";
import Badge from "./ui/Badge";
import type { Document } from "@/types";
import { formatDate } from "@/lib/utils";

interface DocumentListProps {
  documents: Document[];
  onDelete: (id: string) => void;
}

export default function DocumentList({ documents, onDelete }: DocumentListProps) {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusVariant = (
    status: string
  ): "success" | "warning" | "error" | "default" => {
    switch (status) {
      case "ready":
        return "success";
      case "processing":
        return "warning";
      case "failed":
        return "error";
      default:
        return "default";
    }
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="card-hover group relative p-5"
        >
          {/* Delete button */}
          <button
            onClick={() => onDelete(doc.id)}
            className="absolute right-3 top-3 rounded-lg p-1.5 text-gray-600 opacity-0 transition-all hover:bg-red-500/10 hover:text-red-400 group-hover:opacity-100"
            title="Delete document"
          >
            <Trash2 className="h-4 w-4" />
          </button>

          {/* File icon and name */}
          <div className="mb-4 flex items-start gap-3">
            <div className="rounded-xl bg-brand-500/10 p-2.5">
              <FileText className="h-6 w-6 text-brand-400" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="truncate text-sm font-semibold text-white">
                {doc.filename}
              </h3>
              <p className="mt-0.5 text-xs uppercase text-gray-500">
                {doc.file_type}
              </p>
            </div>
          </div>

          {/* Status badge */}
          <div className="mb-4">
            <Badge variant={getStatusVariant(doc.status)}>
              {doc.status}
            </Badge>
          </div>

          {/* Metadata */}
          <div className="space-y-2 text-xs text-gray-500">
            <div className="flex items-center gap-2">
              <Hash className="h-3.5 w-3.5" />
              <span>{doc.chunk_count} chunks</span>
            </div>
            <div className="flex items-center gap-2">
              <HardDrive className="h-3.5 w-3.5" />
              <span>{formatFileSize(doc.file_size)}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-3.5 w-3.5" />
              <span>{formatDate(doc.upload_date)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
