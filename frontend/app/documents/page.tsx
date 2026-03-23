"use client";

import { useState, useEffect } from "react";
import DocumentUpload from "@/components/DocumentUpload";
import DocumentList from "@/components/DocumentList";
import { getDocuments, deleteDocument } from "@/lib/api";
import type { Document } from "@/types";
import { FileText, Upload } from "lucide-react";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setIsLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data.documents);
    } catch (error) {
      console.error("Failed to load documents:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadComplete = () => {
    loadDocuments();
    setShowUpload(false);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (error) {
      console.error("Failed to delete document:", error);
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Documents</h1>
          <p className="mt-1 text-gray-400">
            Upload and manage your document knowledge base
          </p>
        </div>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="btn-primary"
        >
          <Upload className="h-5 w-5" />
          {showUpload ? "Hide Upload" : "Upload Document"}
        </button>
      </div>

      {/* Upload Area */}
      {showUpload && (
        <div className="mb-8 animate-fade-in">
          <DocumentUpload onUploadComplete={handleUploadComplete} />
        </div>
      )}

      {/* Document List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-4">
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
            <p className="text-gray-400">Loading documents...</p>
          </div>
        </div>
      ) : documents.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-700 py-20">
          <FileText className="mb-4 h-16 w-16 text-gray-600" />
          <h3 className="mb-2 text-xl font-semibold text-gray-300">
            No documents yet
          </h3>
          <p className="mb-6 text-gray-500">
            Upload your first document to get started
          </p>
          <button
            onClick={() => setShowUpload(true)}
            className="btn-primary"
          >
            <Upload className="h-5 w-5" />
            Upload Document
          </button>
        </div>
      ) : (
        <DocumentList documents={documents} onDelete={handleDelete} />
      )}
    </div>
  );
}
