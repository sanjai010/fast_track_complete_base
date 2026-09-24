function ChatFAB({ onClick, isOpen }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition-all duration-300 ${
        isOpen
          ? "rotate-0 bg-gray-800 hover:bg-gray-700"
          : "bg-red-600 hover:bg-red-700 hover:scale-105"
      }`}
      aria-label={isOpen ? "Close chat" : "Open chat"}
    >
      {isOpen ? (
        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      ) : (
        <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      )}
    </button>
  );
}

export default ChatFAB;
