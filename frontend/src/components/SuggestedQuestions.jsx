function SuggestedQuestions({ questions, onSelect, disabled }) {
  return (
    <div className="flex flex-wrap gap-2">
      {questions.map((question) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          disabled={disabled}
          className="
            rounded-full
            border
            border-white/15
            bg-white/[0.03]
            px-3.5
            py-2
            text-xs
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
