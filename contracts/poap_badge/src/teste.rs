#![cfg(test)]

use super::*;
use soroban_sdk::{testutils::Address as _, Env, Address, Vec};

/// Helper para criar um ambiente de teste + contrato registrado
fn setup_contract() -> (Env, PoapBadgeClient, Address) {
    let env = Env::default();
    env.mock_all_auths(); // ignora checagem de auth durante testes

    let contract_id = env.register_contract(None, PoapBadge);
    let client = PoapBadgeClient::new(&env, &contract_id);

    let organizer = Address::random(&env);
    (env, client, organizer)
}

#[test]
fn test_create_event_success() {
    let (env, client, organizer) = setup_contract();

    // cria evento
    client.create_event(&1u32, &organizer, &"ipfs://event1".into());

    // verifica que ainda não há colecionadores
    let owners: Vec<Address> = client.list_event_owners(&1u32);
    assert_eq!(owners.len(), 0);
}

#[test]
#[should_panic(expected = "event already exists")]
fn test_create_event_duplicate_should_fail() {
    let (_env, client, organizer) = setup_contract();

    client.create_event(&1u32, &organizer, &"ipfs://event1".into());
    client.create_event(&1u32, &organizer, &"ipfs://event1_dup".into()); // deve falhar
}

#[test]
fn test_mint_badge_success() {
    let (_env, client, organizer) = setup_contract();
    let user = Address::random(&_env);

    client.create_event(&1u32, &organizer, &"ipfs://event1".into());
    client.mint_badge(&1u32, &user);

    assert!(client.has_badge(&1u32, &user));
}

#[test]
#[should_panic(expected = "badge already minted")]
fn test_mint_badge_duplicate_should_fail() {
    let (_env, client, organizer) = setup_contract();
    let user = Address::random(&_env);

    client.create_event(&1u32, &organizer, &"ipfs://event1".into());
    client.mint_badge(&1u32, &user);

    // tentar mintar de novo deve falhar
    client.mint_badge(&1u32, &user);
}

#[test]
#[should_panic(expected = "event does not exist")]
fn test_mint_badge_for_nonexistent_event_should_fail() {
    let (_env, client, _organizer) = setup_contract();
    let user = Address::random(&_env);

    // evento 999 não existe → deve falhar
    client.mint_badge(&999u32, &user);
}

#[test]
fn test_list_user_badges_and_event_owners() {
    let (_env, client, organizer) = setup_contract();
    let user1 = Address::random(&_env);
    let user2 = Address::random(&_env);

    client.create_event(&1u32, &organizer, &"ipfs://event1".into());
    client.create_event(&2u32, &organizer, &"ipfs://event2".into());

    // user1 recebe 2 badges (eventos diferentes)
    client.mint_badge(&1u32, &user1);
    client.mint_badge(&2u32, &user1);

    // user2 recebe 1 badge
    client.mint_badge(&1u32, &user2);

    // listar badges de user1
    let badges_user1: Vec<u32> = client.list_user_badges(&user1);
    assert_eq!(badges_user1.len(), 2);

    // listar colecionadores do evento 1
    let owners_event1: Vec<Address> = client.list_event_owners(&1u32);
    assert_eq!(owners_event1.len(), 2);
    assert!(owners_event1.contains(&user1));
    assert!(owners_event1.contains(&user2));
}

#[test]
fn test_has_badge_returns_false_if_not_minted() {
    let (_env, client, organizer) = setup_contract();
    let user = Address::random(&_env);

    client.create_event(&1u32, &organizer, &"ipfs://event1".into());

    assert!(!client.has_badge(&1u32, &user));
}
