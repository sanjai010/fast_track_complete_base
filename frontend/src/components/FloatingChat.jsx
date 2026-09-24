import { useState, useRef, useEffect } from "react";
import ChatWindow from "./ChatWindow";
import InputBox from "./InputBox";
import SendButton from "./SendButton";
import SuggestedQuestions from "./SuggestedQuestions";
import LeadForm from "./LeadForm";
import BookingCalendar from "./BookingCalendar";
import QuickActions from "./QuickActions";
import { sendChatMessage } from "../services/chatApi";

const SUGGESTED_QUESTIONS = [
  "What services do you offer?",
  "How much does ceramic coating cost?",
  "I want to book an appointment",
  "What are your studio hours?",
];

function FloatingChat({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      message:
        "Welcome to FastTracks Car Care! I can help you with services, pricing, bookings, and more. How can I assist you today?",
      timestamp: Date.now(),
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [handoffRequired, setHandoffRequired] = useState(false);
  const [leadFormOpen, setLeadFormOpen] = useState(false);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);

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
      const data = await sendChatMessage({ message, history });
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message: data.response || "I wasn't able to generate a response. Let me connect you with our team.",
          timestamp: Date.now(),
        },
      ]);
      if (data.decision === "NOT_CONFIRMED" || data.decision === "HUMAN_HANDOFF") {
        setHandoffRequired(true);
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

  function handleBookingSubmit(details) {
    setBookingOpen(false);
    const dateObj = new Date(details.date + "T00:00:00");
    const formattedDate = dateObj.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

    setMessages((prev) => [
      ...prev,
      { sender: "user", message: `Book appointment for ${details.service || "a service"} on ${formattedDate} at ${details.time}`, timestamp: Date.now() },
      {
        sender: "ai",
        message: `Your appointment request has been received!\n\n**Details:**\n- **Date:** ${formattedDate}\n- **Time:** ${details.time}\n- **Service:** ${details.service || "To be confirmed"}\n- **Vehicle:** ${details.vehicle || "Not specified"}\n- **Name:** ${details.name}\n- **Phone:** ${details.phone}\n\nOur team will confirm your appointment via WhatsApp or phone within the next hour. Is there anything else you'd like to know?`,
        timestamp: Date.now(),
      },
    ]);
  }

  function handleLeadSubmit(form) {
    setLeadFormOpen(false);
    setMessages((prev) => [
      ...prev,
      { sender: "ai", message: "Thank you for sharing your details! Our FastTracks team will review your requirements and follow up with you shortly.", timestamp: Date.now() },
    ]);
  }

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-24 right-4 z-50 flex h-[520px] w-[380px] flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#0b0b0b] shadow-2xl sm:right-6 sm:w-[400px]">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 bg-[#0b0b0b] px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-red-600 text-xs font-bold">
            FT
          </div>
          <div>
            <h3 className="text-sm font-bold">FastTracks AI</h3>
            <p className="text-[10px] text-green-400">Online</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setBookingOpen((prev) => !prev)}
            className={`flex h-8 w-8 items-center justify-center rounded-lg transition ${
              bookingOpen ? "bg-red-600 text-white" : "text-gray-400 hover:bg-white/10 hover:text-white"
            }`}
            title="Book Appointment"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </button>
          <a
            href="tel:+918019065252"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 transition hover:bg-white/10 hover:text-white"
            title="Call Us"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </a>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 transition hover:bg-white/10 hover:text-white"
            title="Close"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <ChatWindow messages={messages} loading={loading} />

      {/* Booking Calendar */}
      {bookingOpen && (
        <div className="px-3 pb-3">
          <BookingCalendar onSubmit={handleBookingSubmit} onClose={() => setBookingOpen(false)} />
        </div>
      )}

      {/* Quick Actions */}
      {showQuickActions && messages.length <= 2 && (
        <div className="px-3 pb-2">
          <QuickActions onAction={handleQuickAction} />
        </div>
      )}

      {/* Suggested Questions */}
      <div className="border-t border-white/10 px-3 py-2">
        <SuggestedQuestions questions={SUGGESTED_QUESTIONS} onSelect={handleSendMessage} disabled={loading} />
      </div>

      {/* Handoff */}
      {handoffRequired && (
        <div className="px-3 pb-2">
          <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/5 px-3 py-2">
            <p className="text-[11px] text-yellow-400">Need specialized help? Call us at +91 80190 65252</p>
          </div>
        </div>
      )}

      {/* Lead Form */}
      <div className="px-3 pb-2">
        <LeadForm onSubmitLead={handleLeadSubmit} isOpen={leadFormOpen} onToggle={() => setLeadFormOpen((prev) => !prev)} />
      </div>

      {/* Input */}
      <div className="border-t border-white/10 p-3">
        <div className="flex gap-2">
          <InputBox value={input} onChange={setInput} onKeyDown={handleKeyDown} disabled={loading} />
          <SendButton onClick={() => handleSendMessage()} disabled={loading || !input.trim()} />
        </div>
      </div>
    </div>
  );
}

export default FloatingChat;
