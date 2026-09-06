export type DocumentStatus = "pending" | "processing" | "ready" | "failed";

export interface DocumentResponse {
  id: string;
  filename: string;
  file_type: string;
  status: DocumentStatus;
  error_message: string | null;
  page_count: number | null;
  chunk_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  document_id: string;
  document_name: string;
  page: number | null;
  snippet: string;
}

export type MessageRole = "user" | "assistant";

export interface MessageResponse {
  id: string;
  role: MessageRole;
  content: string;
  citations: Citation[] | null;
  created_at: string;
}

export interface AskResponse {
  conversation_id: string;
  message: MessageResponse;
}

export interface ConversationResponse {
  id: string;
  document_id: string | null;
  title: string | null;
  created_at: string;
}

export interface ConversationDetailResponse extends ConversationResponse {
  messages: MessageResponse[];
}
