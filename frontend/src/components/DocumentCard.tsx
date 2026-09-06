import { Link } from "react-router-dom";
import type { DocumentResponse } from "../api/types";

const STATUS_STYLES: Record<DocumentResponse["status"], string> = {
  pending: "bg-amber-100 text-amber-700",
  processing: "bg-blue-100 text-blue-700",
  ready: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
};

interface Props {
  document: DocumentResponse;
  onDelete: (id: string) => void;
}

export function DocumentCard({ document, onDelete }: Props) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-slate-900">{document.filename}</p>
        <div className="mt-1 flex items-center gap-2">
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[document.status]}`}>
            {document.status}
          </span>
          {document.chunk_count != null && (
            <span className="text-xs text-slate-400">{document.chunk_count} chunks</span>
          )}
        </div>
        {document.status === "failed" && document.error_message && (
          <p className="mt-1 max-w-md truncate text-xs text-red-600" title={document.error_message}>
            {document.error_message}
          </p>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <Link
          to={document.status === "ready" ? `/documents/${document.id}` : "#"}
          aria-disabled={document.status !== "ready"}
          className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
            document.status === "ready"
              ? "bg-slate-900 text-white hover:bg-slate-800"
              : "cursor-not-allowed bg-slate-100 text-slate-400"
          }`}
        >
          Chat
        </Link>
        <button
          onClick={() => onDelete(document.id)}
          className="rounded-lg px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
