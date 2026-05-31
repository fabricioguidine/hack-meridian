use serde::Serialize;

/// Espelha `EventMetadata` do contrato.
#[derive(Clone, Debug, Serialize, PartialEq, Eq)]
pub struct EventMetadata {
    pub name: String,
    pub description: String,
    pub image_ipfs: String,
}

/// Evento + id hex (32 bytes).
#[derive(Clone, Debug, Serialize, PartialEq, Eq)]
pub struct Event {
    /// `event_id` em hex (64 chars).
    pub id: String,
    #[serde(flatten)]
    pub metadata: EventMetadata,
}
