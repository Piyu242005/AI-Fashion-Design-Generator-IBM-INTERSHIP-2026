/**
 * hooks/useChat.ts — RAG chat hook
 * ==================================
 * Manages local message state and calls the /chat/ endpoint.
 * Keeps an optimistic local history for instant UI updates.
 */

"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { chatApi } from "@/services/api";
import { uuid } from "@/lib/utils";
import type { ChatMessage, ChatRequest } from "@/types";

export function useChat(documentIds: number[]) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const mutation = useMutation({
    mutationFn: (data: ChatRequest) => chatApi.ask(data),
    onMutate: (data) => {
      // Optimistic user bubble
      const userMsg: ChatMessage = {
        id:        uuid(),
        role:      "user",
        content:   data.question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
    },
    onSuccess: (res) => {
      const assistantMsg: ChatMessage = {
        id:        uuid(),
        role:      "assistant",
        content:   res.data.answer,
        sources:   res.data.sources,
        intent:    res.data.intent,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    },
    onError: () => {
      toast.error("Failed to get a response. Please try again.");
      // Remove the optimistic user message on error
      setMessages((prev) => prev.slice(0, -1));
    },
  });

  const sendMessage = (question: string) => {
    if (!question.trim()) return;
    mutation.mutate({ question, document_ids: documentIds });
  };

  const clearChat = () => setMessages([]);

  return {
    messages,
    sendMessage,
    clearChat,
    isThinking: mutation.isPending,
  };
}
