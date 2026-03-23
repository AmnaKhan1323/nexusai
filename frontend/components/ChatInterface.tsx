"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles } from "lucide-react";
import MessageBubble from "./MessageBubble";
import Spinner from "./ui/Spinner";
import { askQuestion } from "@/lib/api";
import type { ChatMessageType, Citation } from "@/types";

interface ChatInterfaceProps {
  messages: ChatMessageType[];
  sessionId: string | null;
  onNewMessage: (
    userMsg: ChatMessageType,
    assistantMsg: ChatMessageType,
    sessionId: string
  ) => void;
}

export default function ChatInterface({
  messages,
  sessionId,
  onNewMessage,
}: ChatInterfaceProps) {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || isLoading) return;

    setInput("");
    setIsLoading(true);

    const userMsg: ChatMessageType = {
      id: `temp-user-${Date.now()}`,
      role: "user",
      content: question,
      citations: null,
      tokens_used: 0,
      created_at: new Date().toISOString(),
    };

    try {
      const response = await askQuestion({
        question,
        session_id: sessionId,
        top_k: 5,
      });

      const assistantMsg: ChatMessageType = {
        id: `temp-assistant-${Date.now()}`,
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        tokens_used: response.tokens_used,
        created_at: new Date().toISOString(),
      };

      onNewMessage(userMsg, assistantMsg, response.session_id);
    } catch (error) {
      const errorMsg: ChatMessageType = {
        id: `temp-error-${Date.now()}`,
        role: "assistant",
        content:
          "I apologize, but I encountered an error processing your question. Please check that documents are uploaded and try again.",
        citations: null,
        tokens_used: 0,
        created_at: new Date().toISOString(),
      };
      onNewMessage(userMsg, errorMsg, sessionId || "");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center">
            <div className="mb-6 rounded-2xl bg-gradient-to-br from-brand-500/20 to-violet-500/20 p-6">
              <Sparkles className="h-12 w-12 text-brand-400" />
            </div>
            <h2 className="mb-2 text-2xl font-bold text-white">
              Ask NexusAI anything
            </h2>
            <p className="max-w-md text-center text-gray-400">
              Ask questions about your uploaded documents. I&apos;ll provide
              accurate answers with source citations.
            </p>
            <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {[
                "What are the key findings in the report?",
                "Summarize the main conclusions",
                "What data supports the recommendations?",
                "Compare the metrics across sections",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="rounded-xl border border-gray-700/50 bg-surface-800/30 px-4 py-3 text-left text-sm text-gray-400 transition-all hover:border-gray-600 hover:bg-surface-800/60 hover:text-gray-300"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-6">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-violet-500">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <div className="rounded-2xl rounded-tl-sm border border-gray-800 bg-surface-800/50 px-4 py-3">
                  <div className="flex gap-1.5">
                    <span className="typing-dot h-2 w-2 rounded-full bg-brand-400" />
                    <span className="typing-dot h-2 w-2 rounded-full bg-brand-400" />
                    <span className="typing-dot h-2 w-2 rounded-full bg-brand-400" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-800 bg-surface-900/50 px-4 py-4 backdrop-blur-xl">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-3xl items-end gap-3"
        >
          <div className="relative flex-1">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your documents..."
              className="input-base max-h-36 min-h-[52px] resize-none pr-4"
              rows={1}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary h-[52px] px-4"
          >
            {isLoading ? (
              <Spinner size="sm" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </form>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-gray-600">
          NexusAI provides answers based on your uploaded documents with
          citations. Verify important information.
        </p>
      </div>
    </div>
  );
}
