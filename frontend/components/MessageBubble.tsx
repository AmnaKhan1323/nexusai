"use client";

import { User, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import CitationCard from "./CitationCard";
import type { ChatMessageType } from "@/types";
import { formatDate } from "@/lib/utils";

interface MessageBubbleProps {
  message: ChatMessageType;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex items-start gap-3 animate-fade-in ${
        isUser ? "flex-row-reverse" : ""
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg ${
          isUser
            ? "bg-gradient-to-br from-emerald-500 to-teal-500"
            : "bg-gradient-to-br from-brand-500 to-violet-500"
        }`}
      >
        {isUser ? (
          <User className="h-4 w-4 text-white" />
        ) : (
          <Sparkles className="h-4 w-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`max-w-[80%] space-y-3 ${isUser ? "items-end" : "items-start"}`}
      >
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "rounded-tr-sm bg-brand-600 text-white"
              : "rounded-tl-sm border border-gray-800 bg-surface-800/50 text-gray-200"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose-nexus">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Citations */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-gray-500">
              Sources ({message.citations.length})
            </p>
            <div className="grid gap-2">
              {message.citations.map((citation, idx) => (
                <CitationCard key={idx} citation={citation} index={idx + 1} />
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <p
          className={`text-xs text-gray-600 ${isUser ? "text-right" : "text-left"}`}
        >
          {formatDate(message.created_at)}
          {!isUser && message.tokens_used > 0 && (
            <span className="ml-2">· {message.tokens_used} tokens</span>
          )}
        </p>
      </div>
    </div>
  );
}
