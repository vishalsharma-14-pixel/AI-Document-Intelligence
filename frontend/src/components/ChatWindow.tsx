import { useEffect, useRef, useState, type FormEvent } from "react";
import type { MessageResponse } from "../api/types";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: MessageResponse[];
  onSend: (message: string) => Promise<void>;
  sending: boolean;
}

export function ChatWindow({ messages, onSend, sending }: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const message = input.trim();
    if (!message || sending) return;
    setInput("");
    await onSend(message);
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-3 overflow-y-auto px-1 py-4">
        {messages.length === 0 && (
          <p className="text-center text-sm text-slate-400">Ask a question about this document to get started.</p>
        )}
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {sending && <p className="text-sm text-slate-400">Thinking…</p>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 pt-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this document…"
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-900"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
