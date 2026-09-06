import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { askQuestion } from "../api/chat";
import { apiErrorMessage } from "../api/client";
import { getDocument, summarizeDocument } from "../api/documents";
import { ChatWindow } from "../components/ChatWindow";
import type { DocumentResponse, MessageResponse } from "../api/types";

export default function DocumentChat() {
  const { id } = useParams<{ id: string }>();
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [summarizing, setSummarizing] = useState(false);

  useEffect(() => {
    if (id) getDocument(id).then(setDocument);
  }, [id]);

  async function handleSend(message: string) {
    if (!id) return;
    setError(null);
    setMessages((prev) => [
      ...prev,
      { id: `temp-${Date.now()}`, role: "user", content: message, citations: null, created_at: new Date().toISOString() },
    ]);
    setSending(true);
    try {
      const res = await askQuestion({ message, documentId: id, conversationId });
      setConversationId(res.conversation_id);
      setMessages((prev) => [...prev, res.message]);
    } catch (err) {
      setError(apiErrorMessage(err, "Failed to get a response"));
    } finally {
      setSending(false);
    }
  }

  async function handleSummarize() {
    if (!id) return;
    setSummarizing(true);
    setError(null);
    try {
      setSummary(await summarizeDocument(id));
    } catch (err) {
      setError(apiErrorMessage(err, "Failed to summarize document"));
    } finally {
      setSummarizing(false);
    }
  }

  return (
    <div className="flex h-screen flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <div className="min-w-0">
            <Link to="/" className="text-xs font-medium text-slate-400 hover:text-slate-600">
              ← Documents
            </Link>
            <h1 className="truncate text-lg font-semibold text-slate-900">{document?.filename ?? "Loading…"}</h1>
          </div>
          <button
            onClick={handleSummarize}
            disabled={summarizing}
            className="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            {summarizing ? "Summarizing…" : "Summarize"}
          </button>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col overflow-hidden px-6 py-4">
        {summary && (
          <div className="mb-4 rounded-xl border border-slate-200 bg-white p-4">
            <div className="mb-1 flex items-center justify-between">
              <p className="text-sm font-medium text-slate-900">Summary</p>
              <button onClick={() => setSummary(null)} className="text-xs text-slate-400 hover:text-slate-600">
                Dismiss
              </button>
            </div>
            <p className="text-sm text-slate-600">{summary}</p>
          </div>
        )}
        {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
        <ChatWindow messages={messages} onSend={handleSend} sending={sending} />
      </main>
    </div>
  );
}
