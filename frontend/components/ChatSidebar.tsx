"use client";

import { MessageSquarePlus, MessageSquare, Loader2 } from "lucide-react";
import type { ChatSession } from "@/types";
import { formatDate } from "@/lib/utils";

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  isLoading: boolean;
}

export default function ChatSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  isLoading,
}: ChatSidebarProps) {
  return (
    <div className="flex h-full flex-col border-r border-gray-800 bg-surface-900/50">
      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="flex w-full items-center gap-3 rounded-xl border border-gray-700 bg-surface-800/50 px-4 py-3 text-sm font-medium text-gray-300 transition-all hover:border-brand-500/50 hover:bg-surface-800 hover:text-white"
        >
          <MessageSquarePlus className="h-5 w-5 text-brand-400" />
          New Chat
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {isLoading ? (
          <div className="flex items-center justify-center py-10">
            <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
          </div>
        ) : sessions.length === 0 ? (
          <div className="py-10 text-center text-sm text-gray-500">
            No chat sessions yet
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`group flex w-full flex-col items-start rounded-lg px-3 py-2.5 text-left transition-all ${
                  activeSessionId === session.id
                    ? "bg-brand-500/10 text-white"
                    : "text-gray-400 hover:bg-surface-800/80 hover:text-gray-200"
                }`}
              >
                <div className="flex w-full items-center gap-2">
                  <MessageSquare
                    className={`h-4 w-4 flex-shrink-0 ${
                      activeSessionId === session.id
                        ? "text-brand-400"
                        : "text-gray-600"
                    }`}
                  />
                  <span className="truncate text-sm font-medium">
                    {session.title}
                  </span>
                </div>
                <div className="mt-1 flex w-full items-center gap-2 pl-6">
                  <span className="text-xs text-gray-600">
                    {formatDate(session.created_at)}
                  </span>
                  {session.message_count > 0 && (
                    <span className="text-xs text-gray-600">
                      · {session.message_count} msgs
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
