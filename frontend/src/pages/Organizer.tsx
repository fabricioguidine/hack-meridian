import { useState } from "react";

import { config } from "../config";
import { createEvent, mintBadge } from "../contract";
import { eventIdFromSlug } from "../util";
import { useWallet } from "../wallet-context";

export function Organizer() {
  const { address } = useWallet();
  const [slug, setSlug] = useState("meridian-2025");
  const [name, setName] = useState("Meridian 2025");
  const [description, setDescription] = useState(
    "Attended the Stellar Meridian conference",
  );
  const [imageIpfs, setImageIpfs] = useState("ipfs://");
  const [recipient, setRecipient] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  if (!address) {
    return (
      <section>
        <h1>Organizer</h1>
        <p className="muted">
          Connect your wallet to create events and mint badges.
        </p>
      </section>
    );
  }

  if (!config.contractId) {
    return (
      <section>
        <h1>Organizer</h1>
        <p className="error">
          Set <code>VITE_CONTRACT_ID</code> to a deployed contract to enable writes.
        </p>
      </section>
    );
  }

  async function run(fn: () => Promise<string>, label: string) {
    setBusy(true);
    setStatus(null);
    try {
      const hash = await fn();
      setStatus(`${label} ok - tx ${hash}`);
    } catch (e) {
      setStatus(`${label} failed: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  async function onCreate() {
    const id = await eventIdFromSlug(slug);
    await run(
      () => createEvent(address!, id, name, description, imageIpfs),
      "create_event",
    );
  }

  async function onMint() {
    const id = await eventIdFromSlug(slug);
    await run(
      () => mintBadge(address!, id, recipient || address!),
      "mint_badge",
    );
  }

  return (
    <section className="organizer">
      <h1>Organizer</h1>
      <div className="form">
        <h2>Create event</h2>
        <label>
          Event slug
          <input value={slug} onChange={(e) => setSlug(e.target.value)} />
        </label>
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          Description
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <label>
          Image (ipfs://…)
          <input value={imageIpfs} onChange={(e) => setImageIpfs(e.target.value)} />
        </label>
        <button className="btn btn--primary" disabled={busy} onClick={onCreate}>
          Create event
        </button>
      </div>
      <div className="form">
        <h2>Mint badge</h2>
        <label>
          Recipient (G…, blank = you)
          <input value={recipient} onChange={(e) => setRecipient(e.target.value)} />
        </label>
        <button className="btn btn--accent" disabled={busy} onClick={onMint}>
          Mint badge
        </button>
      </div>
      {status && <p className="status">{status}</p>}
    </section>
  );
}
