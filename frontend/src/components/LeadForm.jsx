import { useState } from "react";

function LeadForm({ onSubmitLead, isOpen, onToggle, light = false }) {
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

  const panelClass = light
    ? "rounded-xl border border-gray-100 bg-gray-50"
    : "rounded-xl border border-white/10 bg-white/[0.03]";

  const toggleClass = light
    ? "flex w-full items-center justify-between px-4 py-3 text-left text-gray-700 transition hover:bg-gray-100"
    : "flex w-full items-center justify-between px-4 py-3 text-left transition hover:bg-white/[0.03]";

  const inputClass = light
    ? "w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-red-400"
    : "w-full rounded-lg border border-white/10 bg-black px-4 py-2.5 text-sm text-white outline-none placeholder:text-gray-500 focus:border-red-500";

  return (
    <div className={panelClass}>
      {/* Toggle Header */}
      <button
        type="button"
        onClick={onToggle}
        className={toggleClass}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm">Share your details</span>
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
              light ? "bg-red-100 text-red-600" : "bg-red-500/20 text-red-400"
            }`}
          >
            Optional
          </span>
        </div>
        <svg
          className={`h-4 w-4 transition-transform ${
            light ? "text-gray-400" : "text-gray-500"
          } ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Collapsible Form (animated height via grid rows) */}
      <div
        className={`grid transition-[grid-template-rows] duration-300 ease-out ${
          isOpen ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
        }`}
        aria-hidden={!isOpen}
      >
        <div className="overflow-hidden">
          <form
            onSubmit={handleSubmit}
            className={`space-y-3 border-t px-4 pb-4 pt-3 ${
              light ? "border-gray-100" : "border-white/10"
            }`}
          >
            <p className={`text-xs leading-5 ${light ? "text-gray-500" : "text-gray-500"}`}>
              Share your details and our team will follow up with you.
            </p>

            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Your name"
              required
              tabIndex={isOpen ? 0 : -1}
              className={inputClass}
            />

            <input
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="Phone number"
              required
              tabIndex={isOpen ? 0 : -1}
              className={inputClass}
            />

            <input
              name="vehicle"
              value={form.vehicle}
              onChange={handleChange}
              placeholder="Vehicle model (optional)"
              tabIndex={isOpen ? 0 : -1}
              className={inputClass}
            />

            <input
              name="service"
              value={form.service}
              onChange={handleChange}
              placeholder="Service required (optional)"
              tabIndex={isOpen ? 0 : -1}
              className={inputClass}
            />

            <button
              type="submit"
              tabIndex={isOpen ? 0 : -1}
              className="w-full rounded-lg bg-red-600 py-2.5 text-sm font-bold text-white transition hover:bg-red-700 active:scale-[0.99]"
            >
              Submit
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LeadForm;
