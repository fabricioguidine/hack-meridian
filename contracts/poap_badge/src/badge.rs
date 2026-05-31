use soroban_sdk::{Address, BytesN, Env, Vec};

use crate::error::Error;
use crate::storage;

/// Emite a badge de um evento para `recipient`. Exige a autorização do
/// organizador do evento e impede emissão dupla para o mesmo coletor.
pub fn mint_badge(env: &Env, event_id: BytesN<32>, recipient: Address) -> Result<(), Error> {
    let organizer = storage::get_event_organizer(env, &event_id).ok_or(Error::EventNotFound)?;
    organizer.require_auth();

    if has_badge(env, &event_id, &recipient) {
        return Err(Error::BadgeAlreadyMinted);
    }

    let mut user_badges = storage::get_user_badges(env, &recipient);
    user_badges.push_back(event_id.clone());
    storage::set_user_badges(env, &recipient, &user_badges);

    let mut owners = storage::get_event_owners(env, &event_id);
    owners.push_back(recipient.clone());
    storage::set_event_owners(env, &event_id, &owners);

    Ok(())
}

pub fn has_badge(env: &Env, event_id: &BytesN<32>, user: &Address) -> bool {
    storage::get_user_badges(env, user).contains(event_id)
}

pub fn list_user_badges(env: &Env, user: &Address) -> Vec<BytesN<32>> {
    storage::get_user_badges(env, user)
}
