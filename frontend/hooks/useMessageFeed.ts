"use client";

import { useState, useEffect, useRef } from "react";
import { Message } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useMessageFeed() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    async function fetchInitialMessages() {
      try {
        const response = await fetch(`${API_URL}/api/feed?limit=50`);
        if (!response.ok) {
          throw new Error("Failed to fetch initial messages");
        }
        const data: Message[] = await response.json();
        setMessages(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred");
      } finally {
        setIsLoading(false);
      }
    }

    fetchInitialMessages();

    // Setup WebSocket connection
    const wsURL = `${API_URL.replace(/^http/, 'ws')}/api/feed/stream`;
    ws.current = new WebSocket(wsURL);

    ws.current.onopen = () => {
      console.log("WebSocket connection established");
    };

    ws.current.onmessage = (event) => {
      const newMessage: Message = JSON.parse(event.data);
      setMessages((prevMessages) => [newMessage, ...prevMessages]);
    };

    ws.current.onerror = (event) => {
      console.error("WebSocket error:", event);
      setError("WebSocket connection error.");
    };

    ws.current.onclose = () => {
      console.log("WebSocket connection closed");
    };

    // Cleanup on component unmount
    return () => {
      ws.current?.close();
    };
  }, []);

  return { messages, isLoading, error };
} 