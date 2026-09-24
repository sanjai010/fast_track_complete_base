function formatTime(timestamp) {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function renderMarkdown(text) {
  if (!text) return text;

  let html = text;

  // Bold: **text** or __text__
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__(.*?)__/g, "<strong>$1</strong>");

  // Italic: *text* or _text_
  html = html.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");
  html = html.replace(/(?<!_)_(?!_)(.*?)(?<!_)_(?!_)/g, "<em>$1</em>");

  // Bullet points: lines starting with - or *
  html = html
    .split("\n")
    .map((line) => {
      const trimmed = line.trim();
      if (/^[-*]\s/.test(trimmed)) {
        return `<li class="ml-4 list-disc">${trimmed.replace(/^[-*]\s/, "")}</li>`;
      }
      return line;
    })
    .join("\n");

  // Wrap consecutive <li> in <ul>
  html = html.replace(/((?:<li[^>]*>.*?<\/li>\n?)+)/g, '<ul class="my-1 space-y-0.5">$1</ul>');

  // Line breaks
  html = html.replace(/\n/g, "<br/>");

  return html;
}

function MessageBubble({ sender, message, timestamp }) {
  const isUser = sender === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} message-enter`}>
      <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : "flex-row"} max-w-[85%]`}>
        {/* Avatar */}
        {!isUser && (
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-red-600/20 text-[11px] font-bold text-red-400">
            FT
          </div>
        )}

        <div>
          {/* Bubble */}
          <div
            className={`rounded-2xl px-4 py-3 text-sm leading-6 ${
              isUser
                ? "rounded-br-sm bg-red-600 text-white"
                : "rounded-bl-sm border border-white/10 bg-white/[0.07] text-gray-200"
            }`}
          >
            {isUser ? (
              <span>{message}</span>
            ) : (
              <span dangerouslySetInnerHTML={{ __html: renderMarkdown(message) }} />
            )}
          </div>

          {/* Timestamp */}
          {timestamp && (
            <p
              className={`mt-1 text-[10px] text-gray-600 ${
                isUser ? "text-right" : "text-left"
              }`}
            >
              {formatTime(timestamp)}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;
