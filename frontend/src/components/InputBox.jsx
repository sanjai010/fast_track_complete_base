function InputBox({ value, onChange, onKeyDown, disabled }) {
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