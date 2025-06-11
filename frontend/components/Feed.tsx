"use client";

import { useMessageFeed } from "@/hooks/useMessageFeed";
import MessageCard from "./MessageCard";

export default function Feed() {
  const { messages, isLoading, error } = useMessageFeed();

  if (isLoading) {
    return <p className="text-gray-400">Loading feed...</p>;
  }

  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  return (
    <div className="w-full max-w-2xl">
      {messages.map((message) => (
        <MessageCard key={message.id} message={message} />
      ))}
    </div>
  );
} 