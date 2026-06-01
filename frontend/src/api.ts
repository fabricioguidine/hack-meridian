import { config } from "./config";
import type { Event } from "./types";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${config.backendUrl}${path}`);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listEvents: () => get<string[]>("/events"),
  getEvent: (id: string) => get<Event>(`/events/${id}`),
  eventOwners: (id: string) => get<string[]>(`/events/${id}/owners`),
  gallery: () => get<Event[]>("/gallery"),
  userBadges: (account: string) => get<string[]>(`/users/${account}/badges`),
};
