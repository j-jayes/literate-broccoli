import type { LunchSession, MenuItem, RestaurantMenu } from "./types";

const BASE = "/api";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || res.statusText);
  }
  return res.json();
}

export async function login(password: string): Promise<void> {
  const res = await fetch(`${BASE}/auth`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ password }),
  });
  await handleResponse(res);
}

export async function checkAuth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/auth/check`, { credentials: "include" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function scrapeMenu(
  restaurantName: string,
  menuUrl?: string
): Promise<MenuItem[]> {
  const res = await fetch(`${BASE}/scrape`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ restaurant_name: restaurantName, menu_url: menuUrl || null }),
  });
  const data = await handleResponse<{ items: MenuItem[] }>(res);
  return data.items;
}

export async function getCachedRestaurants(): Promise<RestaurantMenu[]> {
  const res = await fetch(`${BASE}/cached-restaurants`, {
    credentials: "include",
  });
  const data = await handleResponse<{ restaurants: RestaurantMenu[] }>(res);
  return data.restaurants;
}

export async function createSession(
  restaurants: RestaurantMenu[],
  description?: string
): Promise<LunchSession> {
  const res = await fetch(`${BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      restaurants,
      description: description || null,
    }),
  });
  return handleResponse<LunchSession>(res);
}

export async function getSession(sessionId: string): Promise<LunchSession> {
  const res = await fetch(`${BASE}/sessions/${sessionId}`);
  return handleResponse<LunchSession>(res);
}

export async function submitOrder(
  sessionId: string,
  name: string,
  selectedItems: string[]
): Promise<LunchSession> {
  const res = await fetch(`${BASE}/sessions/${sessionId}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, selected_items: selectedItems }),
  });
  return handleResponse<LunchSession>(res);
}

export function getCsvUrl(sessionId: string): string {
  return `${BASE}/sessions/${sessionId}/csv`;
}
