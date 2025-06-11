import { Message } from "@/lib/types";
import { format } from "date-fns";

interface MessageCardProps {
  message: Message;
}

export default function MessageCard({ message }: MessageCardProps) {
  return (
    <div className="w-full p-4 mb-4 bg-gray-800 rounded-lg shadow">
      <div className="flex justify-between items-center mb-2">
        <span className="font-bold text-blue-400">{message.channel.name}</span>
        <span className="text-xs text-gray-400">
          {format(new Date(message.created_at), "HH:mm:ss dd-MMM-yyyy")}
        </span>
      </div>
      <p className="text-gray-300 whitespace-pre-wrap">{message.body}</p>
    </div>
  );
} 