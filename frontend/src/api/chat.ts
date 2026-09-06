import { apiClient } from "./client";
import type { AskResponse, ConversationDetailResponse, ConversationResponse } from "./types";

export async function askQuestion(params: {
  message: string;
  conversationId?: string;
  documentId?: string;
}): Promise<AskResponse> {
  const { data } = await apiClient.post<AskResponse>("/api/chat/ask", {
    message: params.message,
    conversation_id: params.conversationId ?? null,
    document_id: params.documentId ?? null,
  });
  return data;
}

export async function listConversations(): Promise<ConversationResponse[]> {
  const { data } = await apiClient.get<ConversationResponse[]>("/api/chat/conversations");
  return data;
}

export async function getConversation(id: string): Promise<ConversationDetailResponse> {
  const { data } = await apiClient.get<ConversationDetailResponse>(`/api/chat/conversations/${id}`);
  return data;
}
