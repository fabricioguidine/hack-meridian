import { useEffect, useState } from "react";

import { api } from "../api";
import { shortHex } from "../util";
import { useWallet } from "../wallet-context";

export function Collection() {
  const { address } = useWallet();
  const [ids, setIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!address) return;
    api
      .userBadges(address)
      .then(setIds)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, [address]);

  if (!address) {
    return (
      <section>
        <h1>My Badges</h1>
        <p className="muted">Connect your wallet to see your collection.</p>
      </section>
    );
  }

  return (
    <section>
      <h1>My Badges</h1>
      <p className="muted">{address}</p>
      {error && <p className="error">{error}</p>}
      <p className="count">{ids.length} badge(s)</p>
      <ul className="idlist">
        {ids.map((id) => (
          <li key={id}>
            <code>{shortHex(id, 8)}</code>
          </li>
        ))}
      </ul>
    </section>
  );
}
