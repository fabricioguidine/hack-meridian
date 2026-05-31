# poap_badge_api (Rust backend)

Read-only REST API over the `poap_badge` Soroban contract, built with **axum**.
It reads contract state directly from **Soroban RPC** via `getLedgerEntries`, so it
needs no signing key and runs against any deployed instance of the contract.

> Why Rust: the domain model mirrors the contract and the ScVal decoding is shared
> in spirit with the on-chain types. Writes (create_event / mint_badge) require a
> signed transaction and are intentionally out of scope for this read indexer.

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/health` | `{ "status": "ok" }` |
| GET | `/events` | event ids (hex) |
| GET | `/events/:id` | event with metadata |
| GET | `/events/:id/owners` | collector addresses (strkey) |
| GET | `/users/:account/badges` | event ids the account owns |
| GET | `/gallery` | all events with metadata |

`:id` is the 32-byte `event_id` in hex (64 chars). `:account` is a `G...` strkey.

## Configuration

See [`.env.example`](.env.example). `CONTRACT_ID` is required.

| Var | Default | Notes |
|---|---|---|
| `CONTRACT_ID` | - | Deployed contract strkey (`C...`). **Required.** |
| `SOROBAN_RPC_URL` | `https://soroban-testnet.stellar.org` | RPC endpoint. |
| `PORT` | `4000` | HTTP port. |
| `RUST_LOG` | `info` | Log filter. |

## Run

```bash
cd backend
cargo test                       # 11 tests (ScVal codec + handler logic), no network needed
CONTRACT_ID=C... cargo run       # starts the API on :4000
```

Docker (from repo root):

```bash
CONTRACT_ID=C... docker compose up backend
```

## Design

```
src/
├── main.rs        # axum server bootstrap
├── config.rs      # env config
├── routes.rs      # handlers + AppState (+ handler tests via a mock reader)
├── domain.rs      # Event, EventMetadata (serde)
├── error.rs       # AppError -> HTTP status
└── soroban/
    ├── mod.rs     # SorobanReader trait
    ├── scval.rs   # DataKey -> LedgerKey encoding, ScVal -> domain decoding (+ unit tests)
    └── rpc.rs     # getLedgerEntries client implementing SorobanReader
```

The `SorobanReader` trait lets handlers be unit-tested against a mock, and isolates
all XDR/RPC concerns in `soroban/`. The `scval` codec is tested deterministically
(no network), so correctness of the contract-storage encoding is verified offline.
