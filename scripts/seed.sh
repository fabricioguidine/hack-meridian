#!/usr/bin/env bash
# Seed demo data: create an event and mint a badge to the organizer.
#
# Env:
#   STELLAR_IDENTITY  key name      (default: organizer)
#   STELLAR_NETWORK   network       (default: testnet)
#   CONTRACT_ID       deployed id   (default: read from .contract_id)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IDENTITY="${STELLAR_IDENTITY:-organizer}"
NETWORK="${STELLAR_NETWORK:-testnet}"
CONTRACT_ID="${CONTRACT_ID:-$(cat "$ROOT/.contract_id" 2>/dev/null || true)}"

[ -n "$CONTRACT_ID" ] || { echo "set CONTRACT_ID or run scripts/deploy.sh first" >&2; exit 1; }

ORG="$(stellar keys address "$IDENTITY")"
# event_id is the sha256 of the slug, matching the frontend's eventIdFromSlug()
EVENT_ID="$(printf 'meridian-2025' | sha256sum | cut -d' ' -f1)"

echo ">> create_event $EVENT_ID"
stellar contract invoke --id "$CONTRACT_ID" --source "$IDENTITY" --network "$NETWORK" -- \
  create_event \
  --event_id "$EVENT_ID" \
  --organizer "$ORG" \
  --name "Meridian 2025" \
  --description "Attended the Stellar Meridian conference" \
  --image_ipfs "ipfs://QmDemoBadgeImageHash"

echo ">> mint_badge -> $ORG"
stellar contract invoke --id "$CONTRACT_ID" --source "$IDENTITY" --network "$NETWORK" -- \
  mint_badge --event_id "$EVENT_ID" --recipient "$ORG"

echo ">> done - try: curl localhost:4000/gallery"
