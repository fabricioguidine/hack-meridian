#![no_std]

use soroban_sdk::{contract, contractimpl, Env, Address, BytesN, Symbol};

mod storage;
mod badge;
mod event;

// Função FFI para Python
#[no_mangle]
pub extern "C" fn add(left: u64, right: u64) -> u64 {
    left + right
}

// Exemplo FFI: retorna ponteiro para array de badges (strings)
use core::ffi::c_char;

#[no_mangle]
pub extern "C" fn list_user_badges(user_id: u64, out_len: *mut usize) -> *const *const c_char {
    // Exemplo fixo de badges
    const BADGES: [&'static str; 3] = ["badge1", "badge2", "badge3"];
    // Converte para ponteiros C
    static mut BADGE_PTRS: [*const c_char; 3] = [0 as *const c_char; 3];
    for (i, badge) in BADGES.iter().enumerate() {
        unsafe {
            BADGE_PTRS[i] = badge.as_ptr() as *const c_char;
        }
    }
    unsafe {
        *out_len = BADGES.len();
        BADGE_PTRS.as_ptr()
    }
}

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[contract]
pub struct PoapBadge;

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

    pub fn list_user_badges(env: soroban_sdk::Env, user: soroban_sdk::Address) -> soroban_sdk::Vec<soroban_sdk::BytesN<32>> {
        badge::list_user_badges(env, user)
    }

    pub fn list_event_owners(env: soroban_sdk::Env, event_id: soroban_sdk::BytesN<32>) -> soroban_sdk::Vec<soroban_sdk::Address> {
        event::list_event_owners(env, event_id)
    }
}