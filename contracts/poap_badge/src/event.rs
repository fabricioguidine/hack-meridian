use soroban_sdk::{Address, BytesN, Env, String, Vec};

use crate::error::Error;
use crate::storage;
use crate::types::{BadgeInfo, EventMetadata};

/// Cria um novo evento. Falha se o `event_id` já existir.
pub fn create_event(
    env: &Env,
    event_id: BytesN<32>,
    organizer: Address,
    name: String,
    description: String,
    image_ipfs: String,
) -> Result<(), Error> {
    if storage::has_event(env, &event_id) {
        return Err(Error::EventAlreadyExists);
    }

    let metadata = EventMetadata {
        name,
        description,
        image_ipfs,
    };
    storage::set_event_metadata(env, &event_id, &metadata);
    storage::set_event_organizer(env, &event_id, &organizer);
    storage::push_event(env, &event_id);

    Ok(())
}

pub fn get_event_metadata(env: &Env, event_id: &BytesN<32>) -> Result<EventMetadata, Error> {
    storage::get_event_metadata(env, event_id).ok_or(Error::EventNotFound)
}

pub fn list_events(env: &Env) -> Vec<BytesN<32>> {
    storage::get_events(env)
}

/// Galeria: todos os eventos com seus metadados.
pub fn list_all_badges(env: &Env) -> Vec<BadgeInfo> {
    let mut badges = Vec::new(env);
    for event_id in storage::get_events(env).iter() {
        if let Some(metadata) = storage::get_event_metadata(env, &event_id) {
            badges.push_back(BadgeInfo { event_id, metadata });
        }
    }
    badges
}

pub fn list_event_owners(env: &Env, event_id: &BytesN<32>) -> Vec<Address> {
    storage::get_event_owners(env, event_id)
}
