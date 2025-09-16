use soroban_sdk::{Env, Symbol, Address, BytesN, Vec};

use soroban_sdk::{Env, Symbol, Address, BytesN, Vec, contracttype};

use crate::event::{list_events, get_event_metadata, EventMetadata};

#[derive(Clone)]
#[contracttype] // necessário para serializar no Soroban
pub struct BadgeInfo {
    pub event_id: BytesN<32>,
    pub metadata: EventMetadata,
}

// Lista as badges de um usuário
pub fn get_user_badges(env: &Env, user: &Address) -> Vec<BytesN<32>> {
    env.storage()
        .persistent()
        .get(&(Symbol::new(env, "ub"), user.clone()))
        .unwrap_or(Vec::new(env))
}

// Lista todas as badges criadas na galeria
pub fn list_all_badges(env: &Env) -> Vec<BadgeInfo>{
    let mut badges = Vec::new(env);

    let events = list_events(env.clone());

    for event_id in events.iter() {
        let metadata = get_event_metadata(env.clone(), event_id.clone());
        let badge_info = BadgeInfo {
            event_id: event_id.clone(),
            metadata,
        };
        badges.push_back(badge_info);
    }

    badges

}

// |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

// Retorna todos os donos de badges de um evento específico
pub fn get_event_owners(env: &Env, event_id: &BytesN<32>) -> Vec<Address> {
    env.storage()
        .persistent()
        .get(&(Symbol::new(env, "eo"), event_id.clone()))
        .unwrap_or(Vec::new(env))
}

// Define os donos de badges de um evento específico
pub fn set_event_owners(env: &Env, event_id: &BytesN<32>, owners: &Vec<Address>) {
    env.storage()
        .persistent()
        .set(&(Symbol::new(env, "eo"), event_id.clone()), owners);
}

// eo = event_owners
// ub = user_badges
// em = event_metadata
// ev = events_list