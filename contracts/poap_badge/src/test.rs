use soroban_sdk::{
    testutils::{Address as _, AuthorizedFunction},
    Address, BytesN, Env, String, Symbol,
};

use crate::{error::Error, PoapBadge, PoapBadgeClient};

fn eid(env: &Env, n: u8) -> BytesN<32> {
    BytesN::from_array(env, &[n; 32])
}

fn str_(env: &Env, v: &str) -> String {
    String::from_str(env, v)
}

struct Fixture<'a> {
    env: Env,
    client: PoapBadgeClient<'a>,
    contract_id: Address,
    organizer: Address,
}

fn setup<'a>() -> Fixture<'a> {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register(PoapBadge, ());
    let client = PoapBadgeClient::new(&env, &contract_id);
    let organizer = Address::generate(&env);
    Fixture {
        env,
        client,
        contract_id,
        organizer,
    }
}

fn create_demo_event(f: &Fixture, n: u8) -> BytesN<32> {
    let id = eid(&f.env, n);
    f.client.create_event(
        &id,
        &f.organizer,
        &str_(&f.env, "Meridian 2025"),
        &str_(&f.env, "Attended the Stellar Meridian conference"),
        &str_(&f.env, "ipfs://QmDemoBadgeImageHash"),
    );
    id
}

// ----------------------------------------------------------------------------
// Unit tests
// ----------------------------------------------------------------------------

#[test]
fn create_event_persists_metadata() {
    let f = setup();
    let id = create_demo_event(&f, 1);

    let meta = f.client.get_event(&id);
    assert_eq!(meta.name, str_(&f.env, "Meridian 2025"));
    assert_eq!(meta.image_ipfs, str_(&f.env, "ipfs://QmDemoBadgeImageHash"));
    assert_eq!(f.client.list_events().len(), 1);
    assert_eq!(f.client.list_event_owners(&id).len(), 0);
}

#[test]
fn create_event_duplicate_fails() {
    let f = setup();
    create_demo_event(&f, 1);
    assert_eq!(
        f.client.try_create_event(
            &eid(&f.env, 1),
            &f.organizer,
            &str_(&f.env, "dup"),
            &str_(&f.env, "dup"),
            &str_(&f.env, "ipfs://dup"),
        ),
        Err(Ok(Error::EventAlreadyExists))
    );
}

#[test]
fn get_event_missing_fails() {
    let f = setup();
    assert_eq!(
        f.client.try_get_event(&eid(&f.env, 9)),
        Err(Ok(Error::EventNotFound))
    );
}

#[test]
fn mint_badge_success() {
    let f = setup();
    let id = create_demo_event(&f, 1);
    let user = Address::generate(&f.env);

    f.client.mint_badge(&id, &user);

    assert!(f.client.has_badge(&id, &user));
    assert_eq!(f.client.list_user_badges(&user).len(), 1);
    assert_eq!(f.client.total_badges(&user), 1);
    assert!(f.client.list_event_owners(&id).contains(&user));
}

#[test]
fn mint_badge_duplicate_fails() {
    let f = setup();
    let id = create_demo_event(&f, 1);
    let user = Address::generate(&f.env);
    f.client.mint_badge(&id, &user);

    assert_eq!(
        f.client.try_mint_badge(&id, &user),
        Err(Ok(Error::BadgeAlreadyMinted))
    );
    assert_eq!(f.client.list_event_owners(&id).len(), 1);
    assert_eq!(f.client.total_badges(&user), 1);
}

#[test]
fn mint_badge_for_unknown_event_fails() {
    let f = setup();
    let user = Address::generate(&f.env);
    assert_eq!(
        f.client.try_mint_badge(&eid(&f.env, 99), &user),
        Err(Ok(Error::EventNotFound))
    );
}

#[test]
fn has_badge_false_before_mint() {
    let f = setup();
    let id = create_demo_event(&f, 1);
    let user = Address::generate(&f.env);
    assert!(!f.client.has_badge(&id, &user));
    assert_eq!(f.client.total_badges(&user), 0);
}

#[test]
fn gallery_lists_all_events() {
    let f = setup();
    create_demo_event(&f, 1);
    create_demo_event(&f, 2);
    assert_eq!(f.client.list_all_badges().len(), 2);
}

// ----------------------------------------------------------------------------
// Auth tests
// ----------------------------------------------------------------------------

#[test]
fn create_event_requires_organizer_auth() {
    let f = setup();
    let id = eid(&f.env, 7);
    f.client.create_event(
        &id,
        &f.organizer,
        &str_(&f.env, "n"),
        &str_(&f.env, "d"),
        &str_(&f.env, "ipfs://x"),
    );

    let auths = f.env.auths();
    assert_eq!(auths.len(), 1);
    let (addr, invocation) = &auths[0];
    assert_eq!(addr, &f.organizer);
    match &invocation.function {
        AuthorizedFunction::Contract((cid, fname, _)) => {
            assert_eq!(cid, &f.contract_id);
            assert_eq!(fname, &Symbol::new(&f.env, "create_event"));
        }
        _ => panic!("expected a contract authorization"),
    }
}

#[test]
fn mint_badge_is_authorized_by_organizer_not_recipient() {
    let f = setup();
    let id = create_demo_event(&f, 1);
    let user = Address::generate(&f.env);
    f.client.mint_badge(&id, &user);

    let auths = f.env.auths();
    assert_eq!(auths.len(), 1);
    assert_eq!(auths[0].0, f.organizer);
    assert_ne!(auths[0].0, user);
}

// ----------------------------------------------------------------------------
// End-to-end: jornada completa de um POAP
// ----------------------------------------------------------------------------

#[test]
fn e2e_full_poap_journey() {
    let f = setup();

    // 1. Organizador cria dois eventos (dois dias da conferência).
    let day1 = create_demo_event(&f, 10);
    let day2 = eid(&f.env, 11);
    f.client.create_event(
        &day2,
        &f.organizer,
        &str_(&f.env, "Meridian 2025 - Day 2"),
        &str_(&f.env, "Workshop day"),
        &str_(&f.env, "ipfs://QmDay2"),
    );
    assert_eq!(f.client.list_events().len(), 2);
    assert_eq!(f.client.list_all_badges().len(), 2);

    // 2. Três participantes.
    let alice = Address::generate(&f.env);
    let bob = Address::generate(&f.env);
    let carol = Address::generate(&f.env);

    // 3. Emissão: Alice nos dois dias, Bob só dia 1, Carol só dia 2.
    f.client.mint_badge(&day1, &alice);
    f.client.mint_badge(&day2, &alice);
    f.client.mint_badge(&day1, &bob);
    f.client.mint_badge(&day2, &carol);

    // 4. Coleções individuais (gamificação).
    assert_eq!(f.client.total_badges(&alice), 2);
    assert_eq!(f.client.total_badges(&bob), 1);
    assert_eq!(f.client.total_badges(&carol), 1);

    // 5. Verificação cruzada de posse.
    assert!(f.client.has_badge(&day1, &alice));
    assert!(f.client.has_badge(&day2, &alice));
    assert!(f.client.has_badge(&day1, &bob));
    assert!(!f.client.has_badge(&day2, &bob));
    assert!(!f.client.has_badge(&day1, &carol));
    assert!(f.client.has_badge(&day2, &carol));

    // 6. Coletores por evento.
    let day1_owners = f.client.list_event_owners(&day1);
    assert_eq!(day1_owners.len(), 2);
    assert!(day1_owners.contains(&alice));
    assert!(day1_owners.contains(&bob));

    let day2_owners = f.client.list_event_owners(&day2);
    assert_eq!(day2_owners.len(), 2);
    assert!(day2_owners.contains(&alice));
    assert!(day2_owners.contains(&carol));

    // 7. Idempotência: reemitir para Alice falha e não corrompe estado.
    assert_eq!(
        f.client.try_mint_badge(&day1, &alice),
        Err(Ok(Error::BadgeAlreadyMinted))
    );
    assert_eq!(f.client.list_event_owners(&day1).len(), 2);
    assert_eq!(f.client.total_badges(&alice), 2);
}
