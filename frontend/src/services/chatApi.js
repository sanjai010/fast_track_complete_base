const API_URL = "http://127.0.0.1:8001/chat";

export async function sendChatMessage({
  sessionId = null,
  message,
  history = [],
  customerName = "",
  vehicle = null,
  metadata = {},
}) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      history,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API failed: ${response.status}`);
  }

  const data = await response.json();

  return data;
}
