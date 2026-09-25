function ChatFAB({ onClick, isOpen }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="group fixed bottom-6 right-6 z-[70] flex h-14 w-14 items-center justify-center rounded-full bg-red-600 text-white shadow-xl shadow-black/40 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] hover:scale-110 hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-500/30 active:scale-90"
      aria-label={isOpen ? "Close chat" : "Open chat"}
    >
      {/* Attention ping while closed */}
      {!isOpen && (
        <span className="fab-ping pointer-events-none absolute inset-0 rounded-full border-2 border-red-500" />
      )}

      {/* Crossfading icons: chat bubble <-> chevron down */}
      <span className="relative block h-6 w-6">
        <svg
          className={`absolute inset-0 h-6 w-6 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
            isOpen
              ? "rotate-90 scale-50 opacity-0"
              : "rotate-0 scale-100 opacity-100"
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        <svg
          className={`absolute inset-0 h-6 w-6 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
            isOpen
              ? "rotate-0 scale-100 opacity-100"
              : "-rotate-90 scale-50 opacity-0"
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </span>
    </button>
  );
}

export default ChatFAB;
