import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

function ChatWindow({ messages, loading, light = false }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, loading]);

  return (
    <div
      ref={containerRef}
      className={`flex-1 overflow-y-auto ${
        light ? "ft-scroll bg-white px-4 py-4" : "px-5 py-4"
      }`}
    >
      <div className="space-y-4">
        {messages.map((message, index) => (
          <MessageBubble
            key={index}
            sender={message.sender}
            message={message.message}
            timestamp={message.timestamp}
            light={light}
            showMeta={light && index === 0 && message.sender === "ai"}
          />
        ))}

        {loading && <TypingIndicator light={light} />}
      </div>
    </div>
  );
}

export default ChatWindow;
