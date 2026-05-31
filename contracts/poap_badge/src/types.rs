use soroban_sdk::{contracttype, BytesN, String};

/// Metadados de um evento. O conteúdo rico (imagem, atributos) vive no IPFS;
/// aqui guardamos apenas o necessário para verificação on-chain + o ponteiro IPFS.
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct EventMetadata {
    pub name: String,
    pub description: String,
    /// URI IPFS do metadado/imagem da badge, ex.: `ipfs://Qm...`.
    pub image_ipfs: String,
}

/// Par evento + metadados, usado para montar a galeria de badges.
#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BadgeInfo {
    pub event_id: BytesN<32>,
    pub metadata: EventMetadata,
}
