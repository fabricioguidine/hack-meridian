use soroban_sdk::{contracttype, Address, BytesN, Env, Vec};

use crate::types::EventMetadata;

/// Chaves de armazenamento tipadas. Substituem os tuples de `Symbol` soltos,
/// eliminando o risco de duas partes do código lerem/gravarem chaves divergentes.
#[contracttype]
#[derive(Clone)]
pub enum DataKey {
    /// Lista global de eventos: `Vec<BytesN<32>>`.
    Events,
    /// Metadados do evento: `EventMetadata`.
    EventMeta(BytesN<32>),
    /// Organizador (dono) do evento: `Address`.
    EventOrganizer(BytesN<32>),
    /// Coletores da badge do evento: `Vec<Address>`.
    EventOwners(BytesN<32>),
    /// Badges que um usuário possui: `Vec<BytesN<32>>`.
    UserBadges(Address),
}

pub fn has_event(env: &Env, event_id: &BytesN<32>) -> bool {
    env.storage()
        .persistent()
        .has(&DataKey::EventMeta(event_id.clone()))
}

pub fn set_event_metadata(env: &Env, event_id: &BytesN<32>, metadata: &EventMetadata) {
    env.storage()
        .persistent()
        .set(&DataKey::EventMeta(event_id.clone()), metadata);
}

pub fn get_event_metadata(env: &Env, event_id: &BytesN<32>) -> Option<EventMetadata> {
    env.storage()
        .persistent()
        .get(&DataKey::EventMeta(event_id.clone()))
}

pub fn set_event_organizer(env: &Env, event_id: &BytesN<32>, organizer: &Address) {
    env.storage()
        .persistent()
        .set(&DataKey::EventOrganizer(event_id.clone()), organizer);
}

pub fn get_event_organizer(env: &Env, event_id: &BytesN<32>) -> Option<Address> {
    env.storage()
        .persistent()
        .get(&DataKey::EventOrganizer(event_id.clone()))
}

pub fn get_events(env: &Env) -> Vec<BytesN<32>> {
    env.storage()
        .persistent()
        .get(&DataKey::Events)
        .unwrap_or_else(|| Vec::new(env))
}

pub fn push_event(env: &Env, event_id: &BytesN<32>) {
    let mut events = get_events(env);
    events.push_back(event_id.clone());
    env.storage().persistent().set(&DataKey::Events, &events);
}

pub fn get_event_owners(env: &Env, event_id: &BytesN<32>) -> Vec<Address> {
    env.storage()
        .persistent()
        .get(&DataKey::EventOwners(event_id.clone()))
        .unwrap_or_else(|| Vec::new(env))
}

pub fn set_event_owners(env: &Env, event_id: &BytesN<32>, owners: &Vec<Address>) {
    env.storage()
        .persistent()
        .set(&DataKey::EventOwners(event_id.clone()), owners);
}

pub fn get_user_badges(env: &Env, user: &Address) -> Vec<BytesN<32>> {
    env.storage()
        .persistent()
        .get(&DataKey::UserBadges(user.clone()))
        .unwrap_or_else(|| Vec::new(env))
}

pub fn set_user_badges(env: &Env, user: &Address, badges: &Vec<BytesN<32>>) {
    env.storage()
        .persistent()
        .set(&DataKey::UserBadges(user.clone()), badges);
}
