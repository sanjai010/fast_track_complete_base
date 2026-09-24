import { useState, useMemo } from "react";

const SERVICES = [
  "Ceramic Coating",
  "PPF (Paint Protection Film)",
  "Vinyl Wrapping",
  "Car Detailing",
  "Car Spa",
  "Window Tinting",
  "Interior Customization",
  "Custom Audio",
  "Ambient Lighting",
  "Dashcams & Parking Sensors",
  "SRS Paint Correction",
  "Body Kits / Conversion Kits",
];

const TIME_SLOTS = [
  { label: "10:00 AM", value: "10:00" },
  { label: "11:00 AM", value: "11:00" },
  { label: "12:00 PM", value: "12:00" },
  { label: "2:00 PM", value: "14:00" },
  { label: "3:00 PM", value: "15:00" },
  { label: "4:00 PM", value: "16:00" },
  { label: "5:00 PM", value: "17:00" },
];

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function getDaysInMonth(year, month) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year, month) {
  return new Date(year, month, 1).getDay();
}

function isToday(year, month, day) {
  const today = new Date();
  return (
    today.getFullYear() === year &&
    today.getMonth() === month &&
    today.getDate() === day
  );
}

function isPast(year, month, day) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const check = new Date(year, month, day);
  return check < today;
}

function isSunday(year, month, day) {
  return new Date(year, month, day).getDay() === 0;
}

function BookingCalendar({ onSubmit, onClose }) {
  const today = new Date();
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [service, setService] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [step, setStep] = useState("date");

  const daysInMonth = useMemo(
    () => getDaysInMonth(currentYear, currentMonth),
    [currentYear, currentMonth]
  );

  const firstDay = useMemo(
    () => getFirstDayOfMonth(currentYear, currentMonth),
    [currentYear, currentMonth]
  );

  const calendarDays = useMemo(() => {
    const days = [];
    for (let i = 0; i < firstDay; i++) {
      days.push({ day: null, key: `empty-${i}` });
    }
    for (let d = 1; d <= daysInMonth; d++) {
      days.push({
        day: d,
        key: `${currentYear}-${currentMonth}-${d}`,
        disabled:
          isPast(currentYear, currentMonth, d) ||
          isSunday(currentYear, currentMonth, d),
        today: isToday(currentYear, currentMonth, d),
        selected:
          selectedDate &&
          selectedDate.day === d &&
          selectedDate.month === currentMonth &&
          selectedDate.year === currentYear,
      });
    }
    return days;
  }, [firstDay, daysInMonth, currentYear, currentMonth, selectedDate]);

  function prevMonth() {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear((y) => y - 1);
    } else {
      setCurrentMonth((m) => m - 1);
    }
  }

  function nextMonth() {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear((y) => y + 1);
    } else {
      setCurrentMonth((m) => m + 1);
    }
  }

  function handleDateSelect(dayObj) {
    if (!dayObj || dayObj.disabled) return;
    setSelectedDate({
      day: dayObj.day,
      month: currentMonth,
      year: currentYear,
    });
    setSelectedTime(null);
    setStep("time");
  }

  function handleTimeSelect(slot) {
    setSelectedTime(slot);
    setStep("details");
  }

  function handleSubmit() {
    if (!name.trim() || !phone.trim()) return;

    const dateStr = `${selectedDate.year}-${String(selectedDate.month + 1).padStart(2, "0")}-${String(selectedDate.day).padStart(2, "0")}`;

    onSubmit({
      date: dateStr,
      time: selectedTime.value,
      service,
      vehicle,
      name: name.trim(),
      phone: phone.trim(),
    });
  }

  function formatDate() {
    if (!selectedDate) return "";
    return `${selectedDate.day} ${MONTHS[selectedDate.month]} ${selectedDate.year}`;
  }

  return (
    <div className="rounded-xl border border-white/10 bg-[#0b0b0b]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">Book Appointment</span>
          {step !== "date" && (
            <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] text-red-400">
              Step {step === "time" ? "1" : "2"} of 2
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={onClose}
          className="flex h-6 w-6 items-center justify-center rounded-full text-gray-500 transition hover:bg-white/10 hover:text-white"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="p-4">
        {/* Step: Date Selection */}
        {step === "date" && (
          <div>
            {/* Month Navigation */}
            <div className="mb-4 flex items-center justify-between">
              <button
                type="button"
                onClick={prevMonth}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 transition hover:bg-white/10 hover:text-white"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <span className="text-sm font-semibold">
                {MONTHS[currentMonth]} {currentYear}
              </span>
              <button
                type="button"
                onClick={nextMonth}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 transition hover:bg-white/10 hover:text-white"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            {/* Weekday Headers */}
            <div className="mb-2 grid grid-cols-7 gap-1">
              {WEEKDAYS.map((wd) => (
                <div
                  key={wd}
                  className="py-1 text-center text-[10px] font-semibold uppercase text-gray-500"
                >
                  {wd}
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((dayObj) => (
                <button
                  key={dayObj.key}
                  type="button"
                  disabled={dayObj.disabled}
                  onClick={() => handleDateSelect(dayObj)}
                  className={`
                    relative flex h-9 items-center justify-center rounded-lg text-sm transition
                    ${dayObj.day === null ? "invisible" : ""}
                    ${dayObj.disabled ? "cursor-not-allowed text-gray-700" : "cursor-pointer hover:bg-white/10"}
                    ${dayObj.today ? "font-bold text-red-400" : "text-gray-300"}
                    ${dayObj.selected ? "bg-red-600 text-white hover:bg-red-700" : ""}
                  `}
                >
                  {dayObj.day}
                  {dayObj.today && !dayObj.selected && (
                    <span className="absolute bottom-0.5 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full bg-red-500" />
                  )}
                </button>
              ))}
            </div>

            <p className="mt-3 text-center text-[10px] text-gray-600">
              Sundays closed. Past dates are disabled.
            </p>
          </div>
        )}

        {/* Step: Time Selection */}
        {step === "time" && (
          <div>
            <div className="mb-4 flex items-center gap-2">
              <button
                type="button"
                onClick={() => setStep("date")}
                className="flex h-7 items-center gap-1 rounded-lg bg-white/5 px-2 text-xs text-gray-400 transition hover:bg-white/10 hover:text-white"
              >
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
                Back
              </button>
              <span className="text-xs text-gray-500">{formatDate()}</span>
            </div>

            <p className="mb-3 text-xs font-semibold text-gray-400">
              Select a time slot
            </p>

            <div className="grid grid-cols-2 gap-2">
              {TIME_SLOTS.map((slot) => (
                <button
                  key={slot.value}
                  type="button"
                  onClick={() => handleTimeSelect(slot)}
                  className={`
                    rounded-lg border px-3 py-2.5 text-sm font-medium transition
                    ${
                      selectedTime?.value === slot.value
                        ? "border-red-500 bg-red-600 text-white"
                        : "border-white/10 bg-white/[0.03] text-gray-300 hover:border-red-500/50 hover:bg-red-600/10"
                    }
                  `}
                >
                  {slot.label}
                </button>
              ))}
            </div>

            <p className="mt-3 text-center text-[10px] text-gray-600">
              Standard studio hours: 10:00 AM - 6:00 PM
            </p>
          </div>
        )}

        {/* Step: Details */}
        {step === "details" && (
          <div>
            <div className="mb-4 flex items-center gap-2">
              <button
                type="button"
                onClick={() => setStep("time")}
                className="flex h-7 items-center gap-1 rounded-lg bg-white/5 px-2 text-xs text-gray-400 transition hover:bg-white/10 hover:text-white"
              >
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
                Back
              </button>
              <span className="text-xs text-gray-500">
                {formatDate()} at {selectedTime?.label}
              </span>
            </div>

            <div className="space-y-3">
              {/* Service Selector */}
              <div>
                <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                  Service
                </label>
                <select
                  value={service}
                  onChange={(e) => setService(e.target.value)}
                  className="w-full rounded-lg border border-white/10 bg-black px-3 py-2.5 text-sm text-white outline-none focus:border-red-500"
                >
                  <option value="">Select a service</option>
                  {SERVICES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              {/* Vehicle */}
              <div>
                <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                  Vehicle
                </label>
                <input
                  type="text"
                  value={vehicle}
                  onChange={(e) => setVehicle(e.target.value)}
                  placeholder="e.g. Hyundai Creta 2024"
                  className="w-full rounded-lg border border-white/10 bg-black px-3 py-2.5 text-sm text-white outline-none placeholder:text-gray-600 focus:border-red-500"
                />
              </div>

              {/* Name */}
              <div>
                <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                  Your Name *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Full name"
                  required
                  className="w-full rounded-lg border border-white/10 bg-black px-3 py-2.5 text-sm text-white outline-none placeholder:text-gray-600 focus:border-red-500"
                />
              </div>

              {/* Phone */}
              <div>
                <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 98765 43210"
                  required
                  className="w-full rounded-lg border border-white/10 bg-black px-3 py-2.5 text-sm text-white outline-none placeholder:text-gray-600 focus:border-red-500"
                />
              </div>

              {/* Submit */}
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!name.trim() || !phone.trim()}
                className="w-full rounded-lg bg-red-600 py-3 text-sm font-bold transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Confirm Appointment
              </button>

              <p className="text-center text-[10px] text-gray-600">
                Our team will confirm your appointment via WhatsApp or phone.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BookingCalendar;
