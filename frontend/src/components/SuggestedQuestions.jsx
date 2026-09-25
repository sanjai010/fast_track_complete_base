function SuggestedQuestions({ questions, onSelect, disabled, light = false }) {
  return (
    <div className="flex gap-1.5 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
      {questions.map((question, index) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          disabled={disabled}
          style={{ animationDelay: `${index * 60}ms` }}
          className={`rise-in shrink-0 whitespace-nowrap rounded-full border px-3.5 py-1.5 text-[11px] font-medium transition ${
            light
              ? "border-gray-200 bg-white text-gray-600 hover:border-red-300 hover:bg-red-50 hover:text-red-600"
              : "border-white/15 bg-white/[0.03] text-gray-400 hover:border-red-500/50 hover:bg-red-600/10 hover:text-white"
          } disabled:cursor-not-allowed disabled:opacity-40`}
        >
          {question}
        </button>
      ))}
    </div>
  );
}

export default SuggestedQuestions;
