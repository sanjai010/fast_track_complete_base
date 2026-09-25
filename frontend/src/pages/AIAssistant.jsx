import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import ChatWindow from "../components/ChatWindow";
import InputBox from "../components/InputBox";
import SendButton from "../components/SendButton";
import SuggestedQuestions from "../components/SuggestedQuestions";
import CallButton from "../components/CallButton";
import LeadForm from "../components/LeadForm";
import HandoffMessage from "../components/HandoffMessage";
import BookingCalendar from "../components/BookingCalendar";
import QuickActions from "../components/QuickActions";

import { sendChatMessage, submitBooking } from "../services/chatApi";

const SUGGESTED_QUESTIONS = [
  "What services do you offer?",
  "How much does ceramic coating cost?",
  "I want to book an appointment",
  "What are your studio hours?",
];

// Module scope keeps render pure (no Date.now during render).
const WELCOME_TIMESTAMP = Date.now();

function AIAssistant() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      message:
        "Welcome to FastTracks Car Care! I'm here to help you with information about our services, pricing, bookings, and more. How can I assist you today?",
      timestamp: WELCOME_TIMESTAMP,
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("fasttracks_session_id") || null;
  });
  const [handoffRequired, setHandoffRequired] = useState(false);
  const [customerName, setCustomerName] = useState("");
  const [vehicle, setVehicle] = useState(null);
  const [leadFormOpen, setLeadFormOpen] = useState(false);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);

  async function handleSendMessage(messageFromSuggestion) {
    const message = (messageFromSuggestion ?? input).trim();

    if (!message || loading) return;

    setShowQuickActions(false);

    const userMsg = { sender: "user", message, timestamp: Date.now() };

    setMessages((prev) => [...prev, userMsg]);

    // Build conversation history for the backend (last 10 turns)
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
      const data = await sendChatMessage({
        sessionId,
        message,
        history,
        customerName,
        vehicle,
        metadata: {},
      });

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message:
            data.response ||
            "I wasn't able to generate a response. Let me connect you with our team for assistance.",
          timestamp: Date.now(),
        },
      ]);

      if (data.session_id) {
        setSessionId(data.session_id);
        localStorage.setItem("fasttracks_session_id", data.session_id);
      }

      if (
        data.decision === "NOT_CONFIRMED" ||
        data.decision === "HUMAN_HANDOFF"
      ) {
        setHandoffRequired(true);
      }
    } catch (error) {
      console.error("Chat API error:", error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message:
            "I'm unable to connect to the FastTracks assistant at the moment. Please try again, or you can call our team directly for immediate assistance.",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      handleSendMessage();
    }
  }

  function handleQuickAction(actionId) {
    setShowQuickActions(false);

    if (actionId === "book") {
      setBookingOpen(true);
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message:
            "I'd be happy to help you book an appointment! Please select your preferred date and time below.",
          timestamp: Date.now(),
        },
      ]);
    } else if (actionId === "call") {
      window.location.href = "tel:+918019065252";
    } else if (actionId === "services") {
      handleSendMessage("What services do you offer?");
    } else if (actionId === "directions") {
      window.open(
        "https://www.google.com/maps/search/FastTracks+Car+Care+Jubilee+Hills+Hyderabad",
        "_blank"
      );
    }
  }

  async function handleBookingSubmit(details) {
    setBookingOpen(false);

    const dateObj = new Date(details.date + "T00:00:00");
    const formattedDate = dateObj.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        message: `Book appointment for ${details.service || "a service"} on ${formattedDate} at ${details.time}`,
        timestamp: Date.now(),
      },
      {
        sender: "ai",
        message: "Please give me one moment while I save your booking...",
        timestamp: Date.now(),
      },
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

      const reference = result.reference;
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message: `Your appointment request has been received and saved!\n\n**Details:**\n- **Date:** ${formattedDate}\n- **Time:** ${details.time}\n- **Service:** ${details.service || "To be confirmed"}\n- **Vehicle:** ${details.vehicle || "Not specified"}\n- **Name:** ${details.name}\n- **Phone:** ${details.phone}\n- **Booking reference:** ${reference}\n\nOur team will confirm your appointment via WhatsApp or phone within the next hour. Is there anything else you'd like to know?`,
          timestamp: Date.now(),
        },
      ]);
    } catch (error) {
      console.error("Booking save failed:", error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          message:
            "I couldn't save your booking right now. Please try again, or call us directly at +91 80190 65252 — our team will book it for you.",
          timestamp: Date.now(),
        },
      ]);
    }
  }

  function handleLeadSubmit(form) {
    console.log("Lead form submitted:", form);

    setCustomerName(form.name);
    setVehicle(null);
    setLeadFormOpen(false);

    setMessages((prev) => [
      ...prev,
      {
        sender: "ai",
        message:
          "Thank you for sharing your details! Our FastTracks team will review your requirements and follow up with you shortly.",
        timestamp: Date.now(),
      },
    ]);
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      <Navbar />

      <main className="mx-auto max-w-[1400px] px-4 py-6 sm:px-6 lg:px-8">
        <div className="mb-4">
          <button
            type="button"
            onClick={() => navigate("/")}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm text-gray-300 transition hover:border-red-500 hover:text-white"
          >
            Back to Home
          </button>
        </div>

        {/* Two Column Layout */}
        <div className="flex gap-6">

          {/* Left Side - Info Panel */}
          <div className="hidden w-[340px] flex-shrink-0 lg:block">

            {/* Header */}
            <div className="mb-6">
              <p className="text-xs font-bold uppercase tracking-[0.3em] text-red-500">
                FastTracks Car Care
              </p>
              <h1 className="mt-2 text-2xl font-black">
                AI Assistant
              </h1>
              <p className="mt-2 text-sm leading-6 text-gray-400">
                Ask about our services, pricing, bookings, and more.
              </p>
            </div>

            {/* Quick Info Cards */}
            <div className="space-y-3">
              {/* Studio Hours */}
              <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <div className="mb-2 flex items-center gap-2">
                  <svg className="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-xs font-semibold text-gray-300">Studio Hours</span>
                </div>
                <p className="text-sm text-white">Mon - Sat: 10:00 AM - 6:00 PM</p>
                <p className="text-xs text-gray-500">Sunday: Closed</p>
              </div>

              {/* Location */}
              <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <div className="mb-2 flex items-center gap-2">
                  <svg className="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span className="text-xs font-semibold text-gray-300">Location</span>
                </div>
                <p className="text-sm text-white">Jubilee Hills, Hyderabad</p>
                <a
                  href="https://www.google.com/maps/search/FastTracks+Car+Care+Jubilee+Hills+Hyderabad"
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 inline-block text-xs text-red-400 hover:text-red-300"
                >
                  Get Directions
                </a>
              </div>

              {/* Contact */}
              <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <div className="mb-2 flex items-center gap-2">
                  <svg className="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span className="text-xs font-semibold text-gray-300">Contact</span>
                </div>
                <a
                  href="tel:+918019065252"
                  className="text-sm text-white hover:text-red-400"
                >
                  +91 80190 65252
                </a>
              </div>

              {/* Popular Services */}
              <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <div className="mb-2 flex items-center gap-2">
                  <svg className="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <span className="text-xs font-semibold text-gray-300">Popular Services</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {["Ceramic Coating", "PPF", "Vinyl Wrapping", "Car Detailing", "Window Tinting"].map((s) => (
                    <span key={s} className="rounded-full bg-white/5 px-2.5 py-1 text-[10px] text-gray-400">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Chat Panel */}
          <section className="flex h-[680px] w-full max-w-[600px] flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#0b0b0b] shadow-2xl lg:ml-auto">

          {/* Chat Header */}
          <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
            <div>
              <h2 className="font-bold">FastTracks AI</h2>
              <p className="mt-1 text-xs text-green-400">Online</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setBookingOpen((prev) => !prev)}
                className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-semibold transition ${
                  bookingOpen
                    ? "border-red-500 bg-red-600 text-white"
                    : "border-white/20 text-gray-300 hover:border-red-500 hover:text-white"
                }`}
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="hidden sm:inline">Book</span>
              </button>
              <CallButton />
            </div>
          </div>

          {/* Chat Messages */}
          <ChatWindow messages={messages} loading={loading} />

          {/* Booking Calendar */}
          {bookingOpen && (
            <div className="px-5 pb-4">
              <BookingCalendar
                onSubmit={handleBookingSubmit}
                onClose={() => setBookingOpen(false)}
              />
            </div>
          )}

          {/* Quick Actions */}
          {showQuickActions && messages.length <= 2 && (
            <div className="px-5 pb-3">
              <QuickActions onAction={handleQuickAction} />
            </div>
          )}

          {/* Suggested Questions */}
          <div className="border-t border-white/10 px-5 py-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
              Suggested questions
            </p>
            <SuggestedQuestions
              questions={SUGGESTED_QUESTIONS}
              onSelect={handleSendMessage}
              disabled={loading}
            />
          </div>

          {/* Handoff */}
          {handoffRequired && (
            <div className="px-5 pb-4">
              <HandoffMessage />
            </div>
          )}

          {/* Lead Form - Collapsible */}
          <div className="px-5 pb-4">
            <LeadForm
              onSubmitLead={handleLeadSubmit}
              isOpen={leadFormOpen}
              onToggle={() => setLeadFormOpen((prev) => !prev)}
            />
          </div>

          {/* Input */}
          <div className="border-t border-white/10 p-4">
            <div className="flex gap-3">
              <InputBox
                value={input}
                onChange={setInput}
                onKeyDown={handleKeyDown}
                disabled={loading}
              />
              <SendButton
                onClick={() => handleSendMessage()}
                disabled={loading || !input.trim()}
              />
            </div>
            <p className="mt-3 text-center text-[10px] text-gray-600">
              FastTracks Car Care - AI Assistant
            </p>
          </div>

        </section>

        </div>
      </main>
    </div>
  );
}

export default AIAssistant;
