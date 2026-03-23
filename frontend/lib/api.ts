import axios from "axios";
import type {
  DocumentUploadResponse,
  DocumentListResponse,
  DocumentResponse,
  DocumentChunksResponse,
  ChatRequest,
  ChatResponse,
  ChatSessionListResponse,
  ChatMessagesListResponse,
} from "@/types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "An unexpected error occurred";
    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);
    return Promise.reject(error);
  }
);

// ── Documents ─────────────────────────────────────────

export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<DocumentUploadResponse>("/api/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  });
  return response.data;
}

export async function getDocuments(): Promise<DocumentListResponse> {
  const response = await api.get<DocumentListResponse>("/api/documents/");
  return response.data;
}

export async function getDocument(id: string): Promise<DocumentResponse> {
  const response = await api.get<DocumentResponse>(`/api/documents/${id}`);
  return response.data;
}

export async function deleteDocument(id: string): Promise<void> {
  await api.delete(`/api/documents/${id}`);
}

export async function getDocumentChunks(id: string): Promise<DocumentChunksResponse> {
  const response = await api.get<DocumentChunksResponse>(`/api/documents/${id}/chunks`);
  return response.data;
}

// ── Chat ──────────────────────────────────────────────

export async function askQuestion(request: ChatRequest): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>("/api/chat/ask", request);
  return response.data;
}

export async function getChatSessions(): Promise<ChatSessionListResponse> {
  const response = await api.get<ChatSessionListResponse>("/api/chat/sessions");
  return response.data;
}

export async function getSessionMessages(
  sessionId: string
): Promise<ChatMessagesListResponse> {
  const response = await api.get<ChatMessagesListResponse>(
    `/api/chat/sessions/${sessionId}/messages`
  );
  return response.data;
}

export async function deleteChatSession(sessionId: string): Promise<void> {
  await api.delete(`/api/chat/sessions/${sessionId}`);
}

export default api;
