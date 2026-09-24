import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, loading]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-5 py-4"
    >
      <div className="space-y-4">
        {messages.map((message, index) => (
          <MessageBubble
            key={index}
            sender={message.sender}
            message={message.message}
            timestamp={message.timestamp}
          />
        ))}

        {loading && <TypingIndicator />}
      </div>
    </div>
  );
}

export default ChatWindow;
