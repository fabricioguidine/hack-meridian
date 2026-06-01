export const config = {
  backendUrl: import.meta.env.VITE_BACKEND_URL ?? "http://localhost:4000",
  contractId: import.meta.env.VITE_CONTRACT_ID ?? "",
  rpcUrl:
    import.meta.env.VITE_SOROBAN_RPC_URL ?? "https://soroban-testnet.stellar.org",
  networkPassphrase:
    import.meta.env.VITE_NETWORK_PASSPHRASE ?? "Test SDF Network ; September 2015",
};
