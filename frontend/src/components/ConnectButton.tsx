import { shortHex } from "../util";
import { useWallet } from "../wallet-context";

export function ConnectButton() {
  const { address, connect, connecting, disconnect, error } = useWallet();

  if (address) {
    return (
      <button className="btn btn--ghost" onClick={disconnect} title={address}>
        {shortHex(address, 4)}
      </button>
    );
  }

  return (
    <button
      className="btn btn--primary"
      onClick={connect}
      disabled={connecting}
      title={error ?? "Connect Freighter wallet"}
    >
      {connecting ? "Connecting…" : "Connect Freighter"}
    </button>
  );
}
