import { useState } from "react";

function LeadForm({ onSubmitLead, isOpen, onToggle }) {
  const [form, setForm] = useState({
    name: "",
    phone: "",
    vehicle: "",
    service: "",
  });

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    if (onSubmitLead) {
      onSubmitLead(form);
    }

    setForm({
      name: "",
      phone: "",
      vehicle: "",
      service: "",
    });
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03]">
      {/* Toggle Header */}
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between px-4 py-3 text-left transition hover:bg-white/[0.03]"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm">Share your details</span>
          <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] font-semibold text-red-400">
            Optional
          </span>
        </div>
        <svg
          className={`h-4 w-4 text-gray-500 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Collapsible Form */}
      {isOpen && (
        <form
          onSubmit={handleSubmit}
          className="space-y-3 border-t border-white/10 px-4 pb-4 pt-3"
        >
          <p className="text-xs leading-5 text-gray-500">
            Share your details and our team will follow up with you.
          </p>

          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Your name"
            required
            className="w-full rounded-lg border border-white/10 bg-black px-4 py-2.5 text-sm text-white outline-none placeholder:text-gray-500 focus:border-red-500"
          />

          <input
            name="phone"
            value={form.phone}
            onChange={handleChange}
            placeholder="Phone number"
            required
            className="w-full rounded-lg border border-white/10 bg-black px-4 py-2.5 text-sm text-white outline-none placeholder:text-gray-500 focus:border-red-500"
          />

          <input
            name="vehicle"
            value={form.vehicle}
            onChange={handleChange}
            placeholder="Vehicle model (optional)"
            className="w-full rounded-lg border border-white/10 bg-black px-4 py-2.5 text-sm text-white outline-none placeholder:text-gray-500 focus:border-red-500"
          />

          <input
            name="service"
            value={form.service}
            onChange={handleChange}
            placeholder="Service required (optional)"
            className="w-full rounded-lg border border-white/10 bg-black px-4 py-2.5 text-sm text-white outline-none placeholder:text-gray-500 focus:border-red-500"
          />

          <button
            type="submit"
            className="w-full rounded-lg bg-red-600 py-2.5 text-sm font-bold transition hover:bg-red-700"
          >
            Submit
          </button>
        </form>
      )}
    </div>
  );
}

export default LeadForm;
