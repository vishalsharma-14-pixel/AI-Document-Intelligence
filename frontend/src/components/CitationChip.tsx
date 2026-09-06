import type { Citation } from "../api/types";

export function CitationChip({ citation }: { citation: Citation }) {
  const label = citation.page != null ? `${citation.document_name}, p.${citation.page}` : citation.document_name;
  return (
    <span
      title={citation.snippet}
      className="inline-flex cursor-help items-center rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs text-slate-600"
    >
      {label}
    </span>
  );
}
