const ArrowUpIcon = ({ className }) => (
  <svg
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2.5}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M5 15l7-7 7 7"
    />
  </svg>
);

function SendButton({ onClick, disabled, light = false }) {
  if (light) {
    return (
      <button
        type="button"
        onClick={onClick}
        disabled={disabled}
        aria-label="Send message"
        className="
          flex
          h-9
          w-9
          flex-shrink-0
          items-center
          justify-center
          rounded-full
          bg-red-600
          text-white
          transition-all
          duration-200
          hover:scale-105
          hover:bg-red-700
          active:scale-95
          disabled:cursor-not-allowed
          disabled:bg-gray-200
          disabled:text-gray-400
          disabled:hover:scale-100
        "
      >
        <ArrowUpIcon className="h-4 w-4" />
      </button>
    );
  }

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
        text-white
        transition-all
        duration-200
        hover:bg-red-700
        active:scale-95
        disabled:cursor-not-allowed
        disabled:opacity-40
      "
    >
      <ArrowUpIcon className="h-5 w-5" />
    </button>
  );
}

export default SendButton;
