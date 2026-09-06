import { apiClient } from "./client";
import type { DocumentResponse } from "./types";

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<DocumentResponse>("/api/documents", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listDocuments(): Promise<DocumentResponse[]> {
  const { data } = await apiClient.get<DocumentResponse[]>("/api/documents");
  return data;
}

export async function getDocument(id: string): Promise<DocumentResponse> {
  const { data } = await apiClient.get<DocumentResponse>(`/api/documents/${id}`);
  return data;
}

export async function deleteDocument(id: string): Promise<void> {
  await apiClient.delete(`/api/documents/${id}`);
}

export async function summarizeDocument(id: string): Promise<string> {
  const { data } = await apiClient.post<{ id: string; summary: string }>(`/api/documents/${id}/summary`);
  return data.summary;
}
