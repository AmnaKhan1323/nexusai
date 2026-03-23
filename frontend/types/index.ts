// ── Citation ──────────────────────────────────────────

export interface Citation {
  document_name: string;
  document_id: string;
  chunk_index: number;
  content: string;
  relevance_score: number;
  page_number?: number | null;
}

// ── Documents ─────────────────────────────────────────

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  chunk_count: number;
  total_tokens: number;
  status: string;
}

export interface DocumentUploadResponse {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  message: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface DocumentResponse extends Document {}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  content: string;
  token_count: number;
  page_number?: number | null;
}

export interface DocumentChunksResponse {
  document_id: string;
  filename: string;
  chunks: DocumentChunk[];
  total_chunks: number;
}

// ── Chat ──────────────────────────────────────────────

export interface ChatRequest {
  question: string;
  session_id: string | null;
  top_k?: number;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  session_id: string;
  tokens_used: number;
}

export interface ChatMessageType {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[] | null;
  tokens_used: number;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at?: string | null;
  message_count: number;
}

export interface ChatSessionListResponse {
  sessions: ChatSession[];
  total: number;
}

export interface ChatMessagesListResponse {
  session_id: string;
  messages: ChatMessageType[];
  total: number;
}

// ── Error ─────────────────────────────────────────────

export interface ApiError {
  detail: string;
  error_code?: string;
}
