# scripts

Operational scripts for deploying the contract and seeding demo data.

## Prerequisites

- [Stellar CLI](https://developers.stellar.org/docs/tools/cli) installed.
- A funded identity on testnet:
  ```bash
  stellar keys generate organizer --network testnet --fund
  ```

## POC flow

```bash
# 1. Deploy the contract (writes the id to .contract_id)
./scripts/deploy.sh

# 2. Seed an event + mint a badge to the organizer
./scripts/seed.sh

# 3. Point the backend + frontend at it
export CONTRACT_ID=$(cat .contract_id)
#   backend:  CONTRACT_ID=$CONTRACT_ID cargo run        (in backend/)
#   frontend: set VITE_CONTRACT_ID=$CONTRACT_ID in frontend/.env
```

## IPFS badge art

```bash
PINATA_JWT=... python scripts/pin_ipfs.py badge.png "Meridian 2025" "Attended"
# -> prints ipfs://<cid> to use as the event's image_ipfs
```

## Notes

- `seed.sh` derives `event_id` as `sha256(slug)`, matching the frontend's
  `eventIdFromSlug()`, so an event seeded here resolves to the same id the DApp uses.
- `STELLAR_IDENTITY` and `STELLAR_NETWORK` override the defaults (`organizer`, `testnet`).
