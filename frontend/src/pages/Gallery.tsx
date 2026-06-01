import { useEffect, useState } from "react";

import { api } from "../api";
import { BadgeCard } from "../components/BadgeCard";
import type { Event } from "../types";

export function Gallery() {
  const [events, setEvents] = useState<Event[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .gallery()
      .then(setEvents)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section>
      <h1>Badge Gallery</h1>
      {loading && <p className="muted">Loading…</p>}
      {error && <p className="error">Could not reach the API: {error}</p>}
      {!loading && !error && events.length === 0 && (
        <p className="muted">No events yet. Create one from the Organizer tab.</p>
      )}
      <div className="grid">
        {events.map((e) => (
          <BadgeCard key={e.id} event={e} />
        ))}
      </div>
    </section>
  );
}
