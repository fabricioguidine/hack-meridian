use async_trait::async_trait;
use serde::Deserialize;
use stellar_xdr::curr::{LedgerEntryData, Limits, ReadXdr, ScVal};

use super::scval;
use super::SorobanReader;
use crate::domain::EventMetadata;
use crate::error::AppError;

/// Cliente que lê o storage persistente do contrato via `getLedgerEntries`.
/// Leituras não exigem transação assinada.
pub struct RpcClient {
    http: reqwest::Client,
    rpc_url: String,
    contract: [u8; 32],
}

impl RpcClient {
    pub fn new(rpc_url: impl Into<String>, contract_id: &str) -> Result<Self, AppError> {
        let contract = stellar_strkey::Contract::from_string(contract_id)
            .map_err(|_| AppError::BadRequest("invalid CONTRACT_ID strkey".into()))?
            .0;
        Ok(Self {
            http: reqwest::Client::new(),
            rpc_url: rpc_url.into(),
            contract,
        })
    }

    async fn fetch_value(&self, key: ScVal) -> Result<Option<ScVal>, AppError> {
        let key_b64 = scval::ledger_key_base64(self.contract, key)?;
        let body = serde_json::json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getLedgerEntries",
            "params": { "keys": [key_b64] }
        });
        let resp: RpcEnvelope = self
            .http
            .post(&self.rpc_url)
            .json(&body)
            .send()
            .await
            .map_err(|e| AppError::Rpc(e.to_string()))?
            .json()
            .await
            .map_err(|e| AppError::Rpc(e.to_string()))?;

        if let Some(err) = resp.error {
            return Err(AppError::Rpc(err.message));
        }
        let entries = resp.result.map(|r| r.entries).unwrap_or_default();
        let entry = match entries.into_iter().next() {
            Some(e) => e,
            None => return Ok(None),
        };
        let data = LedgerEntryData::from_xdr_base64(&entry.xdr, Limits::none())
            .map_err(|e| AppError::Decode(format!("ledger entry xdr: {e}")))?;
        match data {
            LedgerEntryData::ContractData(cd) => Ok(Some(cd.val)),
            _ => Err(AppError::Decode("not contract data".into())),
        }
    }
}

#[derive(Deserialize)]
struct RpcEnvelope {
    result: Option<RpcResult>,
    error: Option<RpcError>,
}

#[derive(Deserialize)]
struct RpcResult {
    #[serde(default)]
    entries: Vec<RpcEntry>,
}

#[derive(Deserialize)]
struct RpcEntry {
    #[serde(alias = "dataXdr")]
    xdr: String,
}

#[derive(Deserialize)]
struct RpcError {
    message: String,
}

#[async_trait]
impl SorobanReader for RpcClient {
    async fn list_events(&self) -> Result<Vec<String>, AppError> {
        match self.fetch_value(scval::key_events()?).await? {
            Some(v) => scval::decode_bytes_vec(&v),
            None => Ok(vec![]),
        }
    }

    async fn get_event(&self, id_hex: &str) -> Result<EventMetadata, AppError> {
        let id = scval::parse_id_hex(id_hex)?;
        match self.fetch_value(scval::key_event_meta(id)?).await? {
            Some(v) => scval::decode_event_metadata(&v),
            None => Err(AppError::NotFound),
        }
    }

    async fn event_owners(&self, id_hex: &str) -> Result<Vec<String>, AppError> {
        let id = scval::parse_id_hex(id_hex)?;
        match self.fetch_value(scval::key_event_owners(id)?).await? {
            Some(v) => scval::decode_address_vec(&v),
            None => Ok(vec![]),
        }
    }

    async fn user_badges(&self, account: &str) -> Result<Vec<String>, AppError> {
        let pk = stellar_strkey::ed25519::PublicKey::from_string(account)
            .map_err(|_| AppError::BadRequest("invalid account strkey".into()))?
            .0;
        match self.fetch_value(scval::key_user_badges(pk)?).await? {
            Some(v) => scval::decode_bytes_vec(&v),
            None => Ok(vec![]),
        }
    }
}
