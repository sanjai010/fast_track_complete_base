function SuggestedQuestions({ questions, onSelect, disabled }) {
  return (
    <div className="flex gap-1.5 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
      {questions.map((question) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          disabled={disabled}
          className="
            shrink-0
            whitespace-nowrap
            rounded-full
            border
            border-white/15
            bg-white/[0.03]
            px-3
            py-1
            text-[11px]
            text-gray-400
            transition
            hover:border-red-500/50
            hover:bg-red-600/10
            hover:text-white
            disabled:cursor-not-allowed
            disabled:opacity-40
          "
        >
          {question}
        </button>
      ))}
    </div>
  );
}

export default SuggestedQuestions;
