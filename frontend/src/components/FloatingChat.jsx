import { useState, useRef, useEffect } from "react";
import ChatWindow from "./ChatWindow";
import InputBox from "./InputBox";
import SendButton from "./SendButton";
import SuggestedQuestions from "./SuggestedQuestions";
import LeadForm from "./LeadForm";
import BookingCalendar from "./BookingCalendar";
import QuickActions from "./QuickActions";
import { sendChatMessage, submitBooking } from "../services/chatApi";

const SUGGESTED_QUESTIONS = [
  "What services do you offer?",
  "How much does ceramic coating cost?",
  "I want to book an appointment",
  "What are your studio hours?",
];

// Module scope keeps render pure (no Date.now during render).
const GREETING = {
  sender: "ai",
  message:
    "Welcome to FastTracks Car Care! I can help you with services, pricing, bookings, and more. How can I assist you today?",
  timestamp: Date.now(),
};

function FloatingChat({ isOpen, onClose }) {
  const [messages, setMessages] = useState([GREETING]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("fasttracks_session_id") || null;
  });
  const [handoffRequired, setHandoffRequired] = useState(false);
  const [leadFormOpen, setLeadFormOpen] = useState(false);
  const [showLeadForm, setShowLeadForm] = useState(false);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  const menuRef = useRef(null);

  /* Escape closes menu first, then the panel */
  useEffect(() => {
    if (!isOpen) return;
    function onKey(event) {
      if (event.key === "Escape") {
        if (menuOpen) setMenuOpen(false);
        else onClose();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, menuOpen, onClose]);

  /* Click outside closes the header menu */
  useEffect(() => {
    if (!menuOpen) return;
    function onDown(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [menuOpen]);

  async function handleSendMessage(messageFromSuggestion) {
    const message = (messageFromSuggestion ?? input).trim();
    if (!message || loading) return;

    setShowQuickActions(false);
    setMessages((prev) => [...prev, { sender: "user", message, timestamp: Date.now() }]);

    const history = messages
      .filter((m) => m.sender === "user" || m.sender === "ai")
      .slice(-10)
      .map((m) => ({
        role: m.sender === "user" ? "user" : "assistant",
        content: m.message,
      }));

    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage({ sessionId, message, history });
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message: data.response || "I wasn't able to generate a response. Let me connect you with our team.",
          timestamp: Date.now(),
        },
      ]);
      if (data.session_id) {
        setSessionId(data.session_id);
        localStorage.setItem("fasttracks_session_id", data.session_id);
      }

      if (data.decision === "NOT_CONFIRMED" || data.decision === "HUMAN_HANDOFF") {
        setHandoffRequired(true);
        setShowLeadForm(true);
        setLeadFormOpen(true);
      }
    } catch (error) {
      console.error("Chat API error:", error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message: "I'm unable to connect right now. Please try again or call us at +91 80190 65252.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") handleSendMessage();
  }

  function handleQuickAction(actionId) {
    setShowQuickActions(false);
    if (actionId === "book") {
      setBookingOpen(true);
      setMessages((prev) => [
        ...prev,
        { sender: "ai", message: "I'd be happy to help you book an appointment! Please select your preferred date and time below.", timestamp: Date.now() },
      ]);
    } else if (actionId === "call") {
      window.location.href = "tel:+918019065252";
    } else if (actionId === "services") {
      handleSendMessage("What services do you offer?");
    } else if (actionId === "directions") {
      window.open("https://www.google.com/maps/search/FastTracks+Car+Care+Jubilee+Hills+Hyderabad", "_blank");
    }
  }

  function handleClearChat() {
    setMessages([GREETING]);
    setShowQuickActions(true);
    setHandoffRequired(false);
    setBookingOpen(false);
    setShowLeadForm(false);
    setLeadFormOpen(false);
    setMenuOpen(false);
    setSessionId(null);
    localStorage.removeItem("fasttracks_session_id");
  }

  async function handleBookingSubmit(details) {
    setBookingOpen(false);
    const dateObj = new Date(details.date + "T00:00:00");
    const formattedDate = dateObj.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

    setMessages((prev) => [
      ...prev,
      { sender: "user", message: `Book appointment for ${details.service || "a service"} on ${formattedDate} at ${details.time}`, timestamp: Date.now() },
      { sender: "ai", message: "Please give me one moment while I save your booking...", timestamp: Date.now() },
    ]);

    try {
      const result = await submitBooking({
        name: details.name,
        phone: details.phone,
        service: details.service,
        date: details.date,
        time: details.time,
        vehicle: details.vehicle,
      });

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message: `Your appointment request has been received and saved!\n\n**Details:**\n- **Date:** ${formattedDate}\n- **Time:** ${details.time}\n- **Service:** ${details.service || "To be confirmed"}\n- **Vehicle:** ${details.vehicle || "Not specified"}\n- **Name:** ${details.name}\n- **Phone:** ${details.phone}\n- **Booking reference:** ${result.reference}\n\nOur team will confirm your appointment via WhatsApp or phone within the next hour. Is there anything else you'd like to know?`,
          timestamp: Date.now(),
        },
      ]);
    } catch (error) {
      console.error("Booking save failed:", error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message: "I couldn't save your booking right now. Please try again, or call us directly at +91 80190 65252 — our team will book it for you.",
          timestamp: Date.now(),
        },
      ]);
    }
  }

  function handleLeadSubmit(form) {
    setLeadFormOpen(false);
    setMessages((prev) => [
      ...prev,
      { sender: "ai", message: "Thank you for sharing your details! Our FastTracks team will review your requirements and follow up with you shortly.", timestamp: Date.now() },
    ]);
    // `form` carries the customer details (name/phone) for future use.
    console.log("Lead form submitted:", form);
  }

  const menuItems = [
    {
      id: "book",
      label: "Book appointment",
      icon: (
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      onClick: () => {
        setMenuOpen(false);
        setBookingOpen(true);
        setMessages((prev) => [
          ...prev,
          { sender: "ai", message: "I'd be happy to help you book an appointment! Please select your preferred date and time below.", timestamp: Date.now() },
        ]);
      },
    },
    {
      id: "lead",
      label: "Share my details",
      icon: (
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
      onClick: () => {
        setMenuOpen(false);
        setShowLeadForm(true);
        setLeadFormOpen(true);
      },
    },
    {
      id: "clear",
      label: "Clear conversation",
      icon: (
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      ),
      onClick: handleClearChat,
    },
  ];

  return (
    <div
      className={`fixed bottom-24 right-4 z-[60] flex h-[min(600px,calc(100vh-190px))] w-[calc(100vw-2rem)] max-w-[400px] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-[0_24px_64px_rgba(0,0,0,0.35)] transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] origin-bottom-right sm:right-6 ${
        isOpen
          ? "visible translate-y-0 scale-100 opacity-100"
          : "invisible pointer-events-none translate-y-4 scale-95 opacity-0"
      }`}
      aria-hidden={!isOpen}
    >
      {/* ================= HEADER ================= */}
      <header className="relative flex h-16 flex-shrink-0 items-center gap-3 border-b border-gray-100 bg-white px-4">
        <div className="relative flex-shrink-0">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-600 text-xs font-bold text-white">
            FT
          </div>
          <span className="absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-emerald-500" />
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-gray-900">FastTracks AI</p>
          <p className="truncate text-xs text-gray-500">Typically replies instantly</p>
        </div>

        {/* Options menu (button + dropdown share one ref so outside-click closes correctly) */}
        <div ref={menuRef} className="relative flex items-center">
          <button
            type="button"
            onClick={() => setMenuOpen((prev) => !prev)}
            className="flex h-9 w-9 items-center justify-center rounded-full text-gray-500 transition hover:bg-gray-100 hover:text-gray-900 active:scale-90"
            aria-label="More options"
            aria-expanded={menuOpen}
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="5" cy="12" r="2" />
              <circle cx="12" cy="12" r="2" />
              <circle cx="19" cy="12" r="2" />
            </svg>
          </button>

          {menuOpen && (
            <div className="pop-in absolute right-0 top-full z-20 mt-1 w-52 origin-top-right overflow-hidden rounded-xl border border-gray-200 bg-white py-1 shadow-xl shadow-black/10">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={item.onClick}
                  className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm text-gray-700 transition hover:bg-gray-50 hover:text-gray-900"
                >
                  <span className="text-gray-400">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={onClose}
          className="flex h-9 w-9 items-center justify-center rounded-full text-gray-500 transition hover:bg-gray-100 hover:text-gray-900 active:scale-90"
          aria-label="Close chat"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      {/* ================= MESSAGES ================= */}
      <ChatWindow messages={messages} loading={loading} light />

      {/* Booking Calendar */}
      {bookingOpen && (
        <div className="rise-in border-t border-gray-100 px-4 py-3">
          <BookingCalendar light onSubmit={handleBookingSubmit} onClose={() => setBookingOpen(false)} />
        </div>
      )}

      {/* Quick Actions (only while the conversation is new) */}
      {showQuickActions && messages.length <= 2 && (
        <div className="border-t border-gray-100 px-4 py-3">
          <QuickActions light onAction={handleQuickAction} />
        </div>
      )}

      {/* Suggested Questions (right after the first exchange, then tidy away) */}
      {messages.length > 2 && messages.length <= 6 && (
        <div className="border-t border-gray-100 px-4 py-2.5">
          <SuggestedQuestions
            light
            questions={SUGGESTED_QUESTIONS}
            onSelect={handleSendMessage}
            disabled={loading}
          />
        </div>
      )}

      {/* Handoff banner */}
      {handoffRequired && (
        <div className="rise-in border-t border-gray-100 px-4 py-2.5">
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5">
            <p className="text-[11px] font-medium leading-4 text-amber-700">
              Need specialized help?{" "}
              <a href="tel:+918019065252" className="underline hover:text-amber-900">
                Call us at +91 80190 65252
              </a>
            </p>
          </div>
        </div>
      )}

      {/* Lead Form (opt-in via menu, or auto after handoff) */}
      {showLeadForm && (
        <div className="border-t border-gray-100 px-4 py-3">
          <LeadForm
            light
            onSubmitLead={handleLeadSubmit}
            isOpen={leadFormOpen}
            onToggle={() => setLeadFormOpen((prev) => !prev)}
          />
        </div>
      )}

      {/* ================= INPUT ================= */}
      <div className="flex-shrink-0 border-t border-gray-100 bg-white px-4 pb-2.5 pt-3">
        <div className="relative flex">
          <InputBox
            light
            value={input}
            onChange={setInput}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <div className="absolute inset-y-0 right-1.5 flex items-center">
            <SendButton light onClick={() => handleSendMessage()} disabled={loading || !input.trim()} />
          </div>
        </div>

        <p className="mt-2 text-center text-[10px] text-gray-400">
          <a href="tel:+918019065252" className="transition hover:text-red-500">
            FastTracks Car Care &middot; +91 80190 65252
          </a>
        </p>
      </div>
    </div>
  );
}

export default FloatingChat;
