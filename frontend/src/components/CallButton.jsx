function CallButton() {
  return (
    <a
      href="tel:+918019065252"
      className="
        flex
        items-center
        justify-center
        gap-2
        rounded-xl
        border
        border-white/20
        px-4
        py-2
        text-sm
        font-semibold
        text-white
        transition
        hover:border-red-500
        hover:bg-red-600
      "
    >
      📞
      <span className="hidden sm:inline">
        Speak to a Specialist
      </span>
    </a>
  );
}

export default CallButton;