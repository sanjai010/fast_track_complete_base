function InputBox({ value, onChange, onKeyDown, disabled, light = false }) {
  if (light) {
    return (
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={onKeyDown}
        disabled={disabled}
        placeholder="Ask a question..."
        className="
          h-12
          min-w-0
          flex-1
          rounded-full
          border
          border-gray-200
          bg-gray-50
          px-5
          pr-14
          text-sm
          text-gray-900
          outline-none
          transition
          placeholder:text-gray-400
          focus:border-red-400
          focus:bg-white
          disabled:opacity-50
        "
      />
    );
  }

  return (
    <input
      type="text"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      onKeyDown={onKeyDown}
      disabled={disabled}
      placeholder="Ask about Fasttracks..."
      className="
        h-14
        min-w-0
        flex-1
        rounded-xl
        border
        border-white/20
        bg-[#111414]
        px-5
        text-sm
        text-white
        outline-none
        placeholder:text-gray-500
        focus:border-red-500
        disabled:opacity-50
      "
    />
  );
}

export default InputBox;
