import { useCallback, useEffect, useRef, useState } from "react";
import { deleteDocument, listDocuments, uploadDocument } from "../api/documents";
import { DocumentCard } from "../components/DocumentCard";
import { UploadDropzone } from "../components/UploadDropzone";
import { useAuth } from "../context/AuthContext";
import type { DocumentResponse } from "../api/types";

const POLL_INTERVAL_MS = 3000;

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const pollRef = useRef<number | null>(null);

  const refresh = useCallback(async () => {
    const docs = await listDocuments();
    setDocuments(docs);
    return docs;
  }, []);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  useEffect(() => {
    const hasActive = documents.some((d) => d.status === "pending" || d.status === "processing");
    if (!hasActive) return;

    pollRef.current = window.setInterval(refresh, POLL_INTERVAL_MS);
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, [documents, refresh]);

  async function handleUpload(file: File) {
    const doc = await uploadDocument(file);
    setDocuments((prev) => [doc, ...prev]);
  }

  async function handleDelete(id: string) {
    setDocuments((prev) => prev.filter((d) => d.id !== id));
    await deleteDocument(id);
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold text-slate-900">AI Document Intelligence</h1>
          <div className="flex items-center gap-3 text-sm text-slate-500">
            <span>{user?.email}</span>
            <button onClick={logout} className="font-medium text-slate-900 hover:underline">
              Log out
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8">
        <UploadDropzone onUpload={handleUpload} />

        <h2 className="mb-3 mt-8 text-sm font-medium text-slate-500">Your documents</h2>
        {loading ? (
          <p className="text-sm text-slate-400">Loading…</p>
        ) : documents.length === 0 ? (
          <p className="text-sm text-slate-400">No documents yet. Upload one to get started.</p>
        ) : (
          <div className="flex flex-col gap-2">
            {documents.map((doc) => (
              <DocumentCard key={doc.id} document={doc} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
