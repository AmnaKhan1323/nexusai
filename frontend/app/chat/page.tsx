"use client";

import { useState, useEffect } from "react";
import ChatInterface from "@/components/ChatInterface";
import ChatSidebar from "@/components/ChatSidebar";
import { getChatSessions, getSessionMessages } from "@/lib/api";
import type { ChatSession, ChatMessageType } from "@/types";

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (activeSessionId) {
      loadMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

  const loadSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const data = await getChatSessions();
      setSessions(data.sessions);
    } catch (error) {
      console.error("Failed to load sessions:", error);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const loadMessages = async (sessionId: string) => {
    try {
      const data = await getSessionMessages(sessionId);
      setMessages(data.messages);
    } catch (error) {
      console.error("Failed to load messages:", error);
    }
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
  };

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
  };

  const handleNewMessage = (
    userMsg: ChatMessageType,
    assistantMsg: ChatMessageType,
    sessionId: string
  ) => {
    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setActiveSessionId(sessionId);
    loadSessions();
  };

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } transition-all duration-300 overflow-hidden`}
      >
        <ChatSidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
          isLoading={isLoadingSessions}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative">
        {/* Toggle sidebar button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute left-3 top-3 z-10 rounded-lg border border-gray-700 bg-surface-800/80 p-2 text-gray-400 backdrop-blur-sm transition-colors hover:bg-surface-700 hover:text-white"
          aria-label="Toggle sidebar"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d={sidebarOpen ? "M11 19l-7-7 7-7" : "M13 5l7 7-7 7"}
            />
          </svg>
        </button>

        <ChatInterface
          messages={messages}
          sessionId={activeSessionId}
          onNewMessage={handleNewMessage}
        />
      </div>
    </div>
  );
}
