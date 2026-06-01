import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "./api";

describe("api client", () => {
  afterEach(() => vi.restoreAllMocks());

  it("gallery returns parsed events", async () => {
    const events = [
      { id: "aa".repeat(32), name: "X", description: "d", image_ipfs: "ipfs://Q" },
    ];
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(events), { status: 200 })),
    );
    const out = await api.gallery();
    expect(out).toHaveLength(1);
    expect(out[0].name).toBe("X");
  });

  it("userBadges hits the right path", async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify([]), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);
    await api.userBadges("GABC");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/users/GABC/badges"),
    );
  });

  it("throws with status on a non-ok response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("boom", { status: 502 })),
    );
    await expect(api.listEvents()).rejects.toThrow(/502/);
  });
});
