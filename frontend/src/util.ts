/** Deterministic 32-byte event id (hex) from a human slug, via SHA-256. */
export async function eventIdFromSlug(slug: string): Promise<string> {
  const data = new TextEncoder().encode(slug);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function hexToBytes(hex: string): Uint8Array {
  const clean = hex.startsWith("0x") ? hex.slice(2) : hex;
  const out = new Uint8Array(clean.length / 2);
  for (let i = 0; i < out.length; i++) {
    out[i] = parseInt(clean.slice(i * 2, i * 2 + 2), 16);
  }
  return out;
}

export function shortHex(value: string, n = 6): string {
  return value.length > n * 2 ? `${value.slice(0, n)}…${value.slice(-n)}` : value;
}

export function ipfsToHttp(uri: string): string {
  return uri.startsWith("ipfs://")
    ? `https://ipfs.io/ipfs/${uri.slice("ipfs://".length)}`
    : uri;
}
