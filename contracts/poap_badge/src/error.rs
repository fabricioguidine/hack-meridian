use soroban_sdk::contracterror;

/// Erros do contrato. Os códigos são estáveis e fazem parte da ABI pública.
#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum Error {
    EventAlreadyExists = 1,
    EventNotFound = 2,
    BadgeAlreadyMinted = 3,
}
