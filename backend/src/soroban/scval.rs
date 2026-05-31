//! Construção das chaves de storage (`DataKey`) e decodificação dos valores
//! `ScVal` para o modelo de domínio. Espelha exatamente como o contrato
//! serializa seus tipos (enum = vec[symbol, ...], struct = map de symbols).

use stellar_xdr::curr::{
    AccountId, ContractDataDurability, Hash, LedgerKey, LedgerKeyContractData, Limits, PublicKey,
    ScAddress, ScBytes, ScMap, ScSymbol, ScVal, ScVec, Uint256, VecM, WriteXdr,
};

use crate::domain::EventMetadata;
use crate::error::AppError;

fn symbol(s: &str) -> Result<ScVal, AppError> {
    let sym = ScSymbol(
        s.as_bytes()
            .to_vec()
            .try_into()
            .map_err(|_| AppError::Decode(format!("symbol too long: {s}")))?,
    );
    Ok(ScVal::Symbol(sym))
}

fn bytes32(raw: [u8; 32]) -> Result<ScVal, AppError> {
    let sb = ScBytes(
        raw.to_vec()
            .try_into()
            .map_err(|_| AppError::Decode("bytes32".into()))?,
    );
    Ok(ScVal::Bytes(sb))
}

/// `DataKey::Events` -> vec[Symbol("Events")]
pub fn key_events() -> Result<ScVal, AppError> {
    enum_unit("Events")
}

/// `DataKey::EventMeta(id)` -> vec[Symbol("EventMeta"), Bytes(id)]
pub fn key_event_meta(id: [u8; 32]) -> Result<ScVal, AppError> {
    enum_one("EventMeta", bytes32(id)?)
}

/// `DataKey::EventOwners(id)` -> vec[Symbol("EventOwners"), Bytes(id)]
pub fn key_event_owners(id: [u8; 32]) -> Result<ScVal, AppError> {
    enum_one("EventOwners", bytes32(id)?)
}

/// `DataKey::UserBadges(addr)` -> vec[Symbol("UserBadges"), Address(addr)]
pub fn key_user_badges(account: [u8; 32]) -> Result<ScVal, AppError> {
    let addr = ScVal::Address(ScAddress::Account(AccountId(
        PublicKey::PublicKeyTypeEd25519(Uint256(account)),
    )));
    enum_one("UserBadges", addr)
}

fn enum_unit(variant: &str) -> Result<ScVal, AppError> {
    sc_vec(vec![symbol(variant)?])
}

fn enum_one(variant: &str, field: ScVal) -> Result<ScVal, AppError> {
    sc_vec(vec![symbol(variant)?, field])
}

fn sc_vec(items: Vec<ScVal>) -> Result<ScVal, AppError> {
    let v: VecM<ScVal> = items
        .try_into()
        .map_err(|_| AppError::Decode("scvec".into()))?;
    Ok(ScVal::Vec(Some(ScVec(v))))
}

/// Monta a `LedgerKey::ContractData` persistente para uma chave do contrato.
pub fn ledger_key(contract: [u8; 32], key: ScVal) -> LedgerKey {
    LedgerKey::ContractData(LedgerKeyContractData {
        contract: ScAddress::Contract(Hash(contract)),
        key,
        durability: ContractDataDurability::Persistent,
    })
}

pub fn ledger_key_base64(contract: [u8; 32], key: ScVal) -> Result<String, AppError> {
    ledger_key(contract, key)
        .to_xdr_base64(Limits::none())
        .map_err(|e| AppError::Decode(format!("xdr encode: {e}")))
}

// ---------------------------------------------------------------------------
// Decodificação ScVal -> domínio
// ---------------------------------------------------------------------------

fn hex(bytes: &[u8]) -> String {
    let mut s = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        s.push_str(&format!("{b:02x}"));
    }
    s
}

fn as_bytes32_hex(v: &ScVal) -> Result<String, AppError> {
    match v {
        ScVal::Bytes(b) => Ok(hex(b.0.as_slice())),
        _ => Err(AppError::Decode("expected bytes".into())),
    }
}

fn as_string(v: &ScVal) -> Result<String, AppError> {
    match v {
        ScVal::String(s) => Ok(String::from_utf8_lossy(s.0.as_slice()).into_owned()),
        _ => Err(AppError::Decode("expected string".into())),
    }
}

fn as_account_strkey(v: &ScVal) -> Result<String, AppError> {
    match v {
        ScVal::Address(ScAddress::Account(AccountId(PublicKey::PublicKeyTypeEd25519(Uint256(
            k,
        ))))) => Ok(stellar_strkey::ed25519::PublicKey(*k).to_string()),
        ScVal::Address(ScAddress::Contract(Hash(h))) => {
            Ok(stellar_strkey::Contract(*h).to_string())
        }
        _ => Err(AppError::Decode("expected address".into())),
    }
}

/// `Vec<BytesN<32>>` -> hex strings.
pub fn decode_bytes_vec(v: &ScVal) -> Result<Vec<String>, AppError> {
    match v {
        ScVal::Vec(Some(items)) => items.0.iter().map(as_bytes32_hex).collect(),
        ScVal::Vec(None) => Ok(vec![]),
        _ => Err(AppError::Decode("expected vec".into())),
    }
}

/// `Vec<Address>` -> strkeys.
pub fn decode_address_vec(v: &ScVal) -> Result<Vec<String>, AppError> {
    match v {
        ScVal::Vec(Some(items)) => items.0.iter().map(as_account_strkey).collect(),
        ScVal::Vec(None) => Ok(vec![]),
        _ => Err(AppError::Decode("expected vec".into())),
    }
}

/// `EventMetadata` (struct = map de symbols).
pub fn decode_event_metadata(v: &ScVal) -> Result<EventMetadata, AppError> {
    let map: &ScMap = match v {
        ScVal::Map(Some(m)) => m,
        _ => return Err(AppError::Decode("expected map".into())),
    };
    let mut name = None;
    let mut description = None;
    let mut image_ipfs = None;
    for entry in map.0.iter() {
        let field = match &entry.key {
            ScVal::Symbol(s) => String::from_utf8_lossy(s.0.as_slice()).into_owned(),
            _ => continue,
        };
        match field.as_str() {
            "name" => name = Some(as_string(&entry.val)?),
            "description" => description = Some(as_string(&entry.val)?),
            "image_ipfs" => image_ipfs = Some(as_string(&entry.val)?),
            _ => {}
        }
    }
    Ok(EventMetadata {
        name: name.ok_or_else(|| AppError::Decode("missing name".into()))?,
        description: description.ok_or_else(|| AppError::Decode("missing description".into()))?,
        image_ipfs: image_ipfs.ok_or_else(|| AppError::Decode("missing image_ipfs".into()))?,
    })
}

/// Converte um `event_id` hex (64 chars) em `[u8; 32]`.
pub fn parse_id_hex(id: &str) -> Result<[u8; 32], AppError> {
    let id = id.strip_prefix("0x").unwrap_or(id);
    if id.len() != 64 {
        return Err(AppError::BadRequest("event id must be 32-byte hex".into()));
    }
    let mut out = [0u8; 32];
    for (i, chunk) in id.as_bytes().chunks(2).enumerate() {
        let s = std::str::from_utf8(chunk).map_err(|_| AppError::BadRequest("bad hex".into()))?;
        out[i] = u8::from_str_radix(s, 16).map_err(|_| AppError::BadRequest("bad hex".into()))?;
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use stellar_xdr::curr::{ScMapEntry, ScString};

    fn scstring(s: &str) -> ScVal {
        ScVal::String(ScString(s.as_bytes().to_vec().try_into().unwrap()))
    }

    #[test]
    fn id_hex_roundtrip() {
        let id = [7u8; 32];
        let h = hex(&id);
        assert_eq!(h.len(), 64);
        assert_eq!(parse_id_hex(&h).unwrap(), id);
    }

    #[test]
    fn parse_id_rejects_bad_length() {
        assert!(parse_id_hex("abcd").is_err());
    }

    #[test]
    fn keys_encode_to_base64() {
        // deterministic, contract-independent: just must not panic and be non-empty
        let b64 = ledger_key_base64([1u8; 32], key_events().unwrap()).unwrap();
        assert!(!b64.is_empty());
        let _ = ledger_key_base64([1u8; 32], key_event_meta([2u8; 32]).unwrap()).unwrap();
        let _ = ledger_key_base64([1u8; 32], key_user_badges([3u8; 32]).unwrap()).unwrap();
    }

    #[test]
    fn decode_metadata_from_map() {
        let entries = vec![
            ScMapEntry {
                key: symbol("name").unwrap(),
                val: scstring("Meridian 2025"),
            },
            ScMapEntry {
                key: symbol("description").unwrap(),
                val: scstring("Attended"),
            },
            ScMapEntry {
                key: symbol("image_ipfs").unwrap(),
                val: scstring("ipfs://Qm"),
            },
        ];
        let map = ScVal::Map(Some(ScMap(entries.try_into().unwrap())));
        let meta = decode_event_metadata(&map).unwrap();
        assert_eq!(meta.name, "Meridian 2025");
        assert_eq!(meta.description, "Attended");
        assert_eq!(meta.image_ipfs, "ipfs://Qm");
    }

    #[test]
    fn decode_bytes_vec_of_ids() {
        let v = sc_vec(vec![bytes32([0xaa; 32]).unwrap(), bytes32([0xbb; 32]).unwrap()]).unwrap();
        let ids = decode_bytes_vec(&v).unwrap();
        assert_eq!(ids.len(), 2);
        assert_eq!(ids[0], "aa".repeat(32));
        assert_eq!(ids[1], "bb".repeat(32));
    }

    #[test]
    fn decode_empty_vec() {
        assert!(decode_bytes_vec(&ScVal::Vec(None)).unwrap().is_empty());
        assert!(decode_address_vec(&ScVal::Vec(None)).unwrap().is_empty());
    }

    #[test]
    fn decode_address_vec_strkeys() {
        let addr = ScVal::Address(ScAddress::Account(AccountId(
            PublicKey::PublicKeyTypeEd25519(Uint256([0u8; 32])),
        )));
        let v = sc_vec(vec![addr]).unwrap();
        let out = decode_address_vec(&v).unwrap();
        assert_eq!(out.len(), 1);
        assert!(out[0].starts_with('G'));
    }
}
