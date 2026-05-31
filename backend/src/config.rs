use std::env;

/// Configuração lida do ambiente. Veja `.env.example`.
#[derive(Clone, Debug)]
pub struct Config {
    /// URL do Soroban RPC (ex.: https://soroban-testnet.stellar.org).
    pub rpc_url: String,
    /// Contract id deployado (strkey `C...`).
    pub contract_id: String,
    /// Porta HTTP do servidor.
    pub port: u16,
}

impl Config {
    pub fn from_env() -> Result<Self, String> {
        let rpc_url = env::var("SOROBAN_RPC_URL")
            .unwrap_or_else(|_| "https://soroban-testnet.stellar.org".to_string());
        let contract_id = env::var("CONTRACT_ID")
            .map_err(|_| "CONTRACT_ID is required (deployed C... strkey)".to_string())?;
        let port = env::var("PORT")
            .ok()
            .and_then(|p| p.parse().ok())
            .unwrap_or(4000);
        Ok(Self {
            rpc_url,
            contract_id,
            port,
        })
    }
}
