#![no_std]

//! POAP-like badge contract on Soroban.
//!
//! Organizadores criam eventos e emitem badges verificáveis (POAP) para os
//! participantes. As badges são imutáveis e ficam on-chain; o conteúdo rico
//! (imagem/atributos) é referenciado via IPFS em [`EventMetadata`].

mod badge;
mod error;
mod event;
mod storage;
mod types;

#[cfg(test)]
mod test;

use soroban_sdk::{contract, contractimpl, Address, BytesN, Env, String, Vec};

use crate::error::Error;
use crate::types::{BadgeInfo, EventMetadata};

#[contract]
pub struct PoapBadge;

#[contractimpl]
impl PoapBadge {
    /// Cria um evento. Exige a autorização do `organizer` e falha se o
    /// `event_id` já existir.
    pub fn create_event(
        env: Env,
        event_id: BytesN<32>,
        organizer: Address,
        name: String,
        description: String,
        image_ipfs: String,
    ) -> Result<(), Error> {
        organizer.require_auth();
        event::create_event(&env, event_id, organizer, name, description, image_ipfs)
    }

    /// Emite a badge do evento para `recipient`. Só o organizador do evento
    /// pode emitir; emissão dupla é rejeitada.
    pub fn mint_badge(env: Env, event_id: BytesN<32>, recipient: Address) -> Result<(), Error> {
        badge::mint_badge(&env, event_id, recipient)
    }

    /// Verifica se `user` possui a badge do evento.
    pub fn has_badge(env: Env, event_id: BytesN<32>, user: Address) -> bool {
        badge::has_badge(&env, &event_id, &user)
    }

    /// Lista as badges (event ids) que `user` possui.
    pub fn list_user_badges(env: Env, user: Address) -> Vec<BytesN<32>> {
        badge::list_user_badges(&env, &user)
    }

    /// Total de badges de `user` (usado pela camada de gamificação).
    pub fn total_badges(env: Env, user: Address) -> u32 {
        badge::list_user_badges(&env, &user).len()
    }

    /// Lista os coletores da badge de um evento.
    pub fn list_event_owners(env: Env, event_id: BytesN<32>) -> Vec<Address> {
        event::list_event_owners(&env, &event_id)
    }

    /// Lista todos os eventos registrados.
    pub fn list_events(env: Env) -> Vec<BytesN<32>> {
        event::list_events(&env)
    }

    /// Galeria: todos os eventos com seus metadados.
    pub fn list_all_badges(env: Env) -> Vec<BadgeInfo> {
        event::list_all_badges(&env)
    }

    /// Metadados de um evento. Falha se o evento não existir.
    pub fn get_event(env: Env, event_id: BytesN<32>) -> Result<EventMetadata, Error> {
        event::get_event_metadata(&env, &event_id)
    }
}
