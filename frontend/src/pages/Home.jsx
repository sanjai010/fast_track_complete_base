import { useState } from "react";
import Navbar from "../components/Navbar";
import FloatingChat from "../components/FloatingChat";
import ChatFAB from "../components/ChatFAB";

function Home() {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar onChatToggle={() => setChatOpen((prev) => !prev)} chatOpen={chatOpen} />

      <main>
        {/* ================= HERO SECTION ================= */}
        <section className="relative min-h-[720px] overflow-hidden lg:min-h-[calc(100vh-82px)]">

          {/* Hero Background Image */}
          <img
            src="/images/hero-car.jpg"
            alt="Fasttracks premium car"
            className="absolute inset-0 h-full w-full object-cover object-[70%_center]"
          />

          {/* Dark Overlay */}
          <div className="absolute inset-0 bg-black/35" />
          <div className="absolute inset-0 bg-gradient-to-r from-black via-black/65 to-black/10" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-transparent to-black/10" />

          {/* ================= HERO CONTENT ================= */}
          <div className="relative z-10 mx-auto flex min-h-[720px] max-w-[1500px] items-center px-6 py-16 sm:px-8 lg:min-h-[calc(100vh-82px)] lg:px-12">

            <div className="w-full max-w-[620px]">

              {/* Location */}
              <p className="mb-4 text-[11px] font-bold uppercase tracking-[0.35em] text-white sm:text-xs">
                Jubilee Hills, Hyderabad
              </p>

              {/* Main Heading */}
              <h1 className="font-black uppercase leading-[0.92] tracking-[-0.03em]">
                <span className="block text-5xl sm:text-6xl md:text-7xl">Premium</span>
                <span className="block text-5xl text-red-600 sm:text-6xl md:text-7xl">Car Care</span>
                <span className="block text-5xl sm:text-6xl md:text-7xl">Services</span>
              </h1>

              {/* Description */}
              <p className="mt-6 max-w-[540px] text-sm leading-6 text-gray-300 sm:text-base sm:leading-7">
                India&apos;s Biggest Instant Car Modification Studio.
                Premium automotive customization, protection, comfort,
                styling and technology under one roof.
              </p>

              {/* ================= CTA BUTTONS ================= */}
              <div className="mt-7 flex flex-wrap gap-3">
                <span className="cursor-default rounded-lg bg-red-600 px-5 py-3.5 text-xs font-bold transition hover:bg-red-700 sm:px-6 sm:py-4 sm:text-sm">
                  BOOK NOW ON WHATSAPP
                </span>
                <span
                  onClick={() => setChatOpen(true)}
                  className="cursor-pointer rounded-lg border border-white/60 px-5 py-3.5 text-xs font-bold transition hover:bg-white hover:text-black sm:px-6 sm:py-4 sm:text-sm"
                >
                  CHAT WITH AI
                </span>
              </div>

              {/* ================= STATS ================= */}
              <div className="mt-10 flex max-w-[540px] items-center border-t border-white/20 pt-6">
                <div className="flex-1">
                  <p className="text-2xl font-black sm:text-3xl">25+</p>
                  <p className="mt-1 text-[10px] uppercase tracking-[0.18em] text-gray-400 sm:text-xs">Years</p>
                </div>
                <div className="mx-5 h-10 w-px bg-white/20 sm:mx-7" />
                <div className="flex-1">
                  <p className="text-2xl font-black sm:text-3xl">12</p>
                  <p className="mt-1 text-[10px] uppercase tracking-[0.18em] text-gray-400 sm:text-xs">Services</p>
                </div>
                <div className="mx-5 h-10 w-px bg-white/20 sm:mx-7" />
                <div className="flex-1">
                  <p className="text-2xl font-black sm:text-3xl">365</p>
                  <p className="mt-1 text-[10px] uppercase tracking-[0.18em] text-gray-400 sm:text-xs">Days Open</p>
                </div>
              </div>

            </div>
          </div>

          {/* ================= SCROLL INDICATOR ================= */}
          <div className="absolute bottom-6 left-1/2 hidden -translate-x-1/2 text-center md:block">
            <div className="mx-auto mb-2 flex h-9 w-5 items-start justify-center rounded-full border border-white/50 pt-2">
              <span className="h-2 w-1 rounded-full bg-red-500" />
            </div>
            <p className="text-[9px] uppercase tracking-[0.3em] text-gray-500">Scroll Down</p>
          </div>

        </section>
      </main>

      {/* ================= FLOATING CHAT ================= */}
      <ChatFAB onClick={() => setChatOpen((prev) => !prev)} isOpen={chatOpen} />
      <FloatingChat isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  );
}

export default Home;
