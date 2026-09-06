import type { MessageResponse } from "../api/types";
import { CitationChip } from "./CitationChip";

export function MessageBubble({ message }: { message: MessageResponse }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 ${isUser ? "bg-slate-900 text-white" : "bg-white border border-slate-200 text-slate-900"}`}>
        <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {message.citations.map((c, i) => (
              <CitationChip key={i} citation={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
