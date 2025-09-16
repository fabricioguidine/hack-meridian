#![no_std]

use soroban_sdk::{contract, contractimpl, Env, Address, BytesN, Symbol};

mod storage;
mod badge;
mod event;

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}

#[contract]
pub struct PoapBadge;

// Cria um evento
#[contractimpl]
impl PoapBadge {
    // importa funções de event.rs
    pub fn create_event(
        env: Env,
        event_id: BytesN<32>,
        organizer: Address,
        name: Symbol,
        description: Symbol,
        image: Symbol,
    ) {
        event::create_event(
            env,
            event_id,
            organizer,
            name,
            description,
            image,
        );
    }

    // importa funções de badge.rs
    pub fn mint_badge(env: soroban_sdk::Env, event_id: soroban_sdk::BytesN<32>, recipient: soroban_sdk::Address) {
        badge::mint_badge(env, event_id, recipient);
    }

    // Lista todas as badges associadas a um usuário específico
    pub fn list_user_badges(env: soroban_sdk::Env, user: soroban_sdk::Address) -> soroban_sdk::Vec<soroban_sdk::BytesN<32>> {
        badge::list_user_badges(env, user)
    }

    // Lista todos os usuários que possuem o badge de um evento específico
    pub fn list_event_owners(env: soroban_sdk::Env, event_id: soroban_sdk::BytesN<32>) -> soroban_sdk::Vec<soroban_sdk::Address> {
        event::list_event_owners(env, event_id)
    }
}