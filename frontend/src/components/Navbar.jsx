import { Link, useLocation } from "react-router-dom";

function Navbar({ onChatToggle, chatOpen }) {
  const location = useLocation();
  const isHome = location.pathname === "/";

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-black/95 backdrop-blur-xl">
      <nav className="mx-auto flex h-[82px] max-w-[1500px] items-center justify-between px-5 lg:px-8">

        {/* Logo */}
        <Link to="/" className="flex-shrink-0">
          <img
            src="/images/fasttracks-logo.png"
            alt="Fasttracks Car Care"
            className="h-[52px] w-auto object-contain sm:h-[58px]"
          />
        </Link>

        {/* Navigation */}
        <div className="hidden items-center gap-8 lg:flex">
          <Link to="/" className={`cursor-default text-sm font-semibold ${isHome ? "text-red-500" : "text-white"}`}>
            Home
          </Link>
          <span className="cursor-default text-sm font-semibold text-white">Services</span>
          <span className="cursor-default text-sm font-semibold text-white">Recliners</span>
          <span className="cursor-default text-sm font-semibold text-white">About</span>
          <span className="cursor-default text-sm font-semibold text-white">Contact</span>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3">
          <span className="hidden cursor-default rounded-lg bg-red-600 px-5 py-3 text-sm font-bold sm:block">
            Book Now
          </span>

          <button
            type="button"
            onClick={onChatToggle}
            className={`rounded-lg border px-4 py-3 text-sm font-bold transition sm:px-5 ${
              chatOpen
                ? "border-red-500 bg-red-600"
                : "border-white/40 hover:border-red-500 hover:bg-red-600"
            }`}
          >
            {chatOpen ? "Close Chat" : "AI Assistant"}
          </button>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
