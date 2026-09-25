const API_URL = "http://127.0.0.1:8001/chat";
const BOOKINGS_URL = "http://127.0.0.1:8001/bookings";

export async function sendChatMessage({
  sessionId = null,
  message,
  history = [],
}) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      history,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API failed: ${response.status}`);
  }

  const data = await response.json();

  return data;
}

export async function submitBooking({
  name = "",
  phone = "",
  service = "",
  date = "",
  time = "",
  vehicle = "",
}) {
  const response = await fetch(BOOKINGS_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      phone,
      service,
      date,
      time,
      vehicle,
    }),
  });

  if (!response.ok) {
    throw new Error(`Booking API failed: ${response.status}`);
  }

  const data = await response.json();

  return data;
}
