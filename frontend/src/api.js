const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

function authHeaders() {
  const token = localStorage.getItem("sokocater_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleRes(res) {
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) {
    localStorage.removeItem("sokocater_token");
    localStorage.removeItem("sokocater_user");
    if (!window.location.pathname.includes("/login")) window.location.href = "/login";
  }
  if (!res.ok) throw new Error(data.message || data.error || "Request failed");
  return data;
}

export async function getCaterers() {
  const res = await fetch(`${API_URL}/caterers`, { headers: authHeaders() });
  return handleRes(res);
}
export async function getBookings() {
  const res = await fetch(`${API_URL}/bookings`, { headers: authHeaders() });
  return handleRes(res);
}
export async function createBooking(payload) {
  const res = await fetch(`${API_URL}/bookings`, { method: "POST", headers: authHeaders(), body: JSON.stringify(payload) });
  return handleRes(res);
}
export async function createCaterer(payload) {
  const res = await fetch(`${API_URL}/caterers`, { method: "POST", headers: authHeaders(), body: JSON.stringify(payload) });
  return handleRes(res);
}