use soroban_sdk::{Env, Symbol, Address, BytesN, Vec};

pub fn get_user_badges(env: &Env, user: &Address) -> Vec<BytesN<32>> {
    env.storage()
        .persistent()
        .get(&(Symbol::new(env, "ub"), user.clone()))
        .unwrap_or(Vec::new(env))
}

pub fn set_user_badges(env: &Env, user: &Address, badges: &Vec<BytesN<32>>) {
    env.storage()
        .persistent()
        .set(&(Symbol::new(env, "ub"), user.clone()), badges);
}

pub fn add_user_badge(env: &Env, user: &Address, badge: &BytesN<32>) {
    let mut badges = get_user_badges(env, user);
    if !badges.contains(badge) {
        badges.push_back(badge.clone());
        set_user_badges(env, user, &badges);
    }
}

// |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

pub fn get_event_owners(env: &Env, event_id: &BytesN<32>) -> Vec<Address> {
    env.storage()
        .persistent()
        .get(&(Symbol::new(env, "eo"), event_id.clone()))
        .unwrap_or(Vec::new(env))
}

pub fn set_event_owners(env: &Env, event_id: &BytesN<32>, owners: &Vec<Address>) {
    env.storage()
        .persistent()
        .set(&(Symbol::new(env, "eo"), event_id.clone()), owners);
}

pub fn add_event_owner(env: &Env, event_id: &BytesN<32>, owner: &Address) {
    let mut owners = get_event_owners(env, event_id);
    if !owners.contains(owner) {
        owners.push_back(owner.clone());
        set_event_owners(env, event_id, &owners);
    }
}

// eo = event_owners
// ub = user_badges
// em = event_metadata
// ev = events_list