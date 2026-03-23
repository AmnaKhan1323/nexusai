"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, FileText, ExternalLink } from "lucide-react";
import type { Citation } from "@/types";
import { truncateText } from "@/lib/utils";

interface CitationCardProps {
  citation: Citation;
  index: number;
}

export default function CitationCard({ citation, index }: CitationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const scorePercent = Math.round(citation.relevance_score * 100);
  const scoreColor =
    scorePercent >= 90
      ? "text-emerald-400 bg-emerald-400/10"
      : scorePercent >= 75
        ? "text-amber-400 bg-amber-400/10"
        : "text-red-400 bg-red-400/10";

  return (
    <div className="overflow-hidden rounded-xl border border-gray-800 bg-surface-800/30 transition-all hover:border-gray-700">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center gap-3 px-3 py-2.5 text-left"
      >
        {/* Index badge */}
        <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-md bg-brand-500/20 text-xs font-bold text-brand-400">
          {index}
        </span>

        {/* Document name */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <FileText className="h-3.5 w-3.5 flex-shrink-0 text-gray-500" />
            <span className="truncate text-sm font-medium text-gray-300">
              {citation.document_name}
            </span>
          </div>
          {!isExpanded && (
            <p className="mt-0.5 truncate text-xs text-gray-500">
              {truncateText(citation.content, 80)}
            </p>
          )}
        </div>

        {/* Score */}
        <span
          className={`flex-shrink-0 rounded-md px-2 py-0.5 text-xs font-semibold ${scoreColor}`}
        >
          {scorePercent}%
        </span>

        {/* Expand icon */}
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 flex-shrink-0 text-gray-500" />
        ) : (
          <ChevronDown className="h-4 w-4 flex-shrink-0 text-gray-500" />
        )}
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="border-t border-gray-800 px-3 py-3">
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-gray-400">
            {citation.content}
          </p>
          <div className="mt-3 flex items-center gap-4 text-xs text-gray-600">
            <span>Chunk #{citation.chunk_index}</span>
            {citation.page_number && (
              <span>Page {citation.page_number}</span>
            )}
            <span>
              Relevance: {(citation.relevance_score * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
