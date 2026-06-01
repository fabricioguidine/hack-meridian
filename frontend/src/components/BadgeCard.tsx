import { Link } from "react-router-dom";

import type { Event } from "../types";
import { ipfsToHttp, shortHex } from "../util";

export function BadgeCard({ event }: { event: Event }) {
  return (
    <Link to={`/event/${event.id}`} className="card">
      <div className="card__art">
        {event.image_ipfs && event.image_ipfs !== "ipfs://" ? (
          <img src={ipfsToHttp(event.image_ipfs)} alt={event.name} loading="lazy" />
        ) : (
          <div className="card__placeholder">◈</div>
        )}
      </div>
      <div className="card__body">
        <h3>{event.name}</h3>
        <p>{event.description}</p>
        <code>{shortHex(event.id, 5)}</code>
      </div>
    </Link>
  );
}
