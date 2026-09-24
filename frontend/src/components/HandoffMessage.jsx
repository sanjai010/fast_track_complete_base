function HandoffMessage() {
  return (
    <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/5 p-4">
      <p className="text-sm font-bold text-yellow-400">
        Connect with Our Team
      </p>

      <p className="mt-1 text-xs leading-5 text-gray-400">
        For detailed pricing, vehicle-specific recommendations, or to
        schedule a consultation, our specialists are ready to assist.
      </p>

      <a
        href="tel:+918019065252"
        className="mt-3 inline-block text-sm font-semibold text-white transition hover:text-red-400"
      >
        Contact FastTracks Specialist
      </a>
    </div>
  );
}

export default HandoffMessage;