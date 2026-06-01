# poap_badge_api (Go backend)

A second implementation of the read API, in **Go** (stdlib `net/http` +
`github.com/stellar/go`), provided side-by-side with the Rust backend for
comparison. Same endpoints, same `getLedgerEntries` read strategy.

## Why this exists

You asked whether Go is applicable. It is - this service compiles and its
ScVal/XDR codec is unit-tested. But note the friction that shows up in practice:

- `github.com/stellar/go` is a **large monorepo module** (pulls Horizon, txnbuild,
  etc.) and requires a recent Go toolchain (**Go >= 1.24**).
- It is **Horizon-oriented**; there is no dedicated Soroban-RPC client, so the
  JSON-RPC call is hand-rolled here. Writes (create/mint) would mean building and
  signing transactions manually.
- The `xdr` optional types (`**ScVec`, `**ScMap`) are awkward compared to the Rust
  SDK's ergonomics.

Net: fine for reads, heavier for a full DApp backend. The Rust service (`../backend`)
remains the recommended one; TypeScript would be the other strong choice.

## Endpoints

Identical to the Rust backend: `/health`, `/events`, `/events/:id`,
`/events/:id/owners`, `/users/:account/badges`, `/gallery`. Default port `4001`.

## Run

```bash
cd backend-go
go test ./...
CONTRACT_ID=C... go run .       # serves on :4001
```

Env: `CONTRACT_ID` (required), `SOROBAN_RPC_URL` (default testnet), `PORT` (4001).

## Layout

```
backend-go/
├── main.go     # bootstrap
├── server.go   # net/http router + handlers (Reader interface)
├── rpc.go      # getLedgerEntries client
├── scval.go    # DataKey -> LedgerKey + ScVal -> domain (stellar/go/xdr)
├── domain.go   # Event / EventMetadata
└── *_test.go   # ScVal codec + handler tests
```
