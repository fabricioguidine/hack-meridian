use soroban_sdk::{Env, Address, BytesN, Symbol, Vec, symbol_short, contracttype};
use crate::storage;

#[derive(Clone)]
#[contracttype]
pub struct EventMetadata {
    pub name: Symbol,
    pub description: Symbol,
    pub image: Symbol, // URL/IPFS hash
}

// Função para criar um novo evento
pub fn create_event(
    env: Env,
    event_id: BytesN<32>,
    organizer: Address,
    name: Symbol,
    description: Symbol,
    image: Symbol,
) {
    // salvar metadados
    let metadata = EventMetadata { name, description, image };
    env.storage().persistent().set(
        &(&symbol_short!("em"), &event_id),
        &metadata,
    );

    // lista global de eventos
    let mut events: Vec<BytesN<32>> = env
        .storage()
        .persistent()
        .get(&symbol_short!("ev"))
        .unwrap_or(Vec::new(&env));

    events.push_back(event_id.clone());
    env.storage().persistent().set(&symbol_short!("ev"), &events);

    // associar organizador
    env.storage().persistent().set(
        &(&symbol_short!("org"), &event_id),
        &organizer,
    );
}

// Listar todos os eventos
pub fn list_events(env: Env) -> Vec<BytesN<32>> {
    env.storage()
        .persistent()
        .get(&symbol_short!("ev"))
        .unwrap_or(Vec::new(&env))
}

// Obter metadados de um evento específico
pub fn get_event_metadata(env: Env, event_id: BytesN<32>) -> EventMetadata {
    env.storage()
        .persistent()
        .get(&(&symbol_short!("em"), &event_id))
        .unwrap()
}

// Listar todos os donos de badges de um evento específico
pub fn list_event_owners(env: Env, event_id: BytesN<32>) -> Vec<Address> {
    storage::get_event_owners(&env, &event_id)
}