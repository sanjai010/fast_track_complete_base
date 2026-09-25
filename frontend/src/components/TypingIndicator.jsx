function TypingIndicator({ light = false }) {
  if (light) {
    return (
      <div className="flex justify-start message-enter">
        <div className="rounded-2xl bg-gray-100 px-4 py-3">
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-gray-400 typing-dot" />
            <span
              className="h-1.5 w-1.5 rounded-full bg-gray-400 typing-dot"
              style={{ animationDelay: "150ms" }}
            />
            <span
              className="h-1.5 w-1.5 rounded-full bg-gray-400 typing-dot"
              style={{ animationDelay: "300ms" }}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start message-enter">
      <div className="flex gap-2.5">
        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-red-600/20 text-[11px] font-bold text-red-400">
          FT
        </div>

        <div className="rounded-2xl rounded-bl-sm border border-white/10 bg-white/[0.07] px-4 py-3">
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-gray-500 typing-dot" />
            <span className="h-1.5 w-1.5 rounded-full bg-gray-500 typing-dot" style={{ animationDelay: "150ms" }} />
            <span className="h-1.5 w-1.5 rounded-full bg-gray-500 typing-dot" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default TypingIndicator;
