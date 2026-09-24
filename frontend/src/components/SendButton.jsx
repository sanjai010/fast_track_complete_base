function SendButton({ onClick, disabled }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label="Send message"
      className="
        flex
        h-14
        w-14
        flex-shrink-0
        items-center
        justify-center
        rounded-xl
        bg-red-600
        text-xl
        font-bold
        transition
        hover:bg-red-700
        disabled:cursor-not-allowed
        disabled:opacity-40
      "
    >
      ➤
    </button>
  );
}

export default SendButton;