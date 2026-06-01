#!/usr/bin/env bash
# Deploy the poap_badge contract to a Soroban network.
#
# Requires the Stellar CLI (https://developers.stellar.org/docs/tools/cli) and a
# funded identity. On testnet you can create+fund one with:
#   stellar keys generate organizer --network testnet --fund
#
# Env:
#   STELLAR_IDENTITY  configured key name   (default: organizer)
#   STELLAR_NETWORK   network name          (default: testnet)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTRACT_DIR="$ROOT/contracts/poap_badge"
IDENTITY="${STELLAR_IDENTITY:-organizer}"
NETWORK="${STELLAR_NETWORK:-testnet}"

echo ">> building wasm"
(cd "$CONTRACT_DIR" && stellar contract build)
WASM="$CONTRACT_DIR/target/wasm32-unknown-unknown/release/poap_badge.wasm"

echo ">> deploying to $NETWORK as $IDENTITY"
CONTRACT_ID=$(stellar contract deploy \
  --wasm "$WASM" \
  --source "$IDENTITY" \
  --network "$NETWORK")

echo "$CONTRACT_ID" > "$ROOT/.contract_id"
echo ">> deployed: $CONTRACT_ID"
echo ">> saved to .contract_id  (export as CONTRACT_ID and VITE_CONTRACT_ID)"
