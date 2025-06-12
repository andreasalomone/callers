import { Message } from "@/lib/types";
import { format } from "date-fns";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface MessageCardProps {
  message: Message;
}

export default function MessageCard({ message }: MessageCardProps) {
  return (
    <Card className="w-full mb-4">
      <CardHeader className="flex flex-row justify-between items-center p-4">
        <CardTitle className="text-base font-bold text-primary">
          {message.channel.name}
        </CardTitle>
        <p className="text-xs text-muted-foreground">
          {format(new Date(message.created_at), "HH:mm:ss dd-MMM-yyyy")}
        </p>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <p className="text-card-foreground whitespace-pre-wrap">{message.body}</p>
      </CardContent>
    </Card>
  );
} 