pub mod rpc;
pub mod scval;

use async_trait::async_trait;

use crate::domain::EventMetadata;
use crate::error::AppError;

/// Leitura do estado do contrato `poap_badge` via Soroban RPC.
#[async_trait]
pub trait SorobanReader: Send + Sync {
    async fn list_events(&self) -> Result<Vec<String>, AppError>;
    async fn get_event(&self, id_hex: &str) -> Result<EventMetadata, AppError>;
    async fn event_owners(&self, id_hex: &str) -> Result<Vec<String>, AppError>;
    async fn user_badges(&self, account: &str) -> Result<Vec<String>, AppError>;
}
