import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api";
import type { Event } from "../types";
import { ipfsToHttp, shortHex } from "../util";

export function EventDetail() {
  const { id = "" } = useParams();
  const [event, setEvent] = useState<Event | null>(null);
  const [owners, setOwners] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getEvent(id)
      .then(setEvent)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    api
      .eventOwners(id)
      .then(setOwners)
      .catch(() => {});
  }, [id]);

  if (error) return <section><p className="error">{error}</p></section>;
  if (!event) return <section><p className="muted">Loading…</p></section>;

  return (
    <section className="detail">
      <div className="detail__art">
        {event.image_ipfs && event.image_ipfs !== "ipfs://" ? (
          <img src={ipfsToHttp(event.image_ipfs)} alt={event.name} />
        ) : (
          <div className="card__placeholder">◈</div>
        )}
      </div>
      <div>
        <h1>{event.name}</h1>
        <p>{event.description}</p>
        <code>{event.id}</code>
        <h2>Collectors ({owners.length})</h2>
        <ul className="idlist">
          {owners.map((o) => (
            <li key={o}>
              <code>{shortHex(o, 8)}</code>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
