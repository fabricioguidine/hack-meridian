package main

import (
	"encoding/hex"
	"fmt"

	"github.com/stellar/go/strkey"
	"github.com/stellar/go/xdr"
)

// --- key construction (mirrors the contract's DataKey enum) ---

func symbol(s string) xdr.ScVal {
	sym := xdr.ScSymbol(s)
	return xdr.ScVal{Type: xdr.ScValTypeScvSymbol, Sym: &sym}
}

func bytes32(b [32]byte) xdr.ScVal {
	sb := xdr.ScBytes(b[:])
	return xdr.ScVal{Type: xdr.ScValTypeScvBytes, Bytes: &sb}
}

func scVec(items ...xdr.ScVal) xdr.ScVal {
	v := xdr.ScVec(items)
	pv := &v
	return xdr.ScVal{Type: xdr.ScValTypeScvVec, Vec: &pv}
}

func keyEvents() xdr.ScVal { return scVec(symbol("Events")) }

func keyEventMeta(id [32]byte) xdr.ScVal {
	return scVec(symbol("EventMeta"), bytes32(id))
}

func keyEventOwners(id [32]byte) xdr.ScVal {
	return scVec(symbol("EventOwners"), bytes32(id))
}

func keyUserBadges(account string) (xdr.ScVal, error) {
	aid, err := xdr.AddressToAccountId(account)
	if err != nil {
		return xdr.ScVal{}, fmt.Errorf("bad account strkey: %w", err)
	}
	addr := xdr.ScAddress{Type: xdr.ScAddressTypeScAddressTypeAccount, AccountId: &aid}
	av := xdr.ScVal{Type: xdr.ScValTypeScvAddress, Address: &addr}
	return scVec(symbol("UserBadges"), av), nil
}

// ledgerKeyB64 builds the persistent ContractData ledger key, base64-encoded.
func ledgerKeyB64(contract [32]byte, key xdr.ScVal) (string, error) {
	var cid xdr.ContractId
	copy(cid[:], contract[:])
	lk := xdr.LedgerKey{
		Type: xdr.LedgerEntryTypeContractData,
		ContractData: &xdr.LedgerKeyContractData{
			Contract:   xdr.ScAddress{Type: xdr.ScAddressTypeScAddressTypeContract, ContractId: &cid},
			Key:        key,
			Durability: xdr.ContractDataDurabilityPersistent,
		},
	}
	return xdr.MarshalBase64(lk)
}

func contractIdFromStrkey(s string) ([32]byte, error) {
	var out [32]byte
	raw, err := strkey.Decode(strkey.VersionByteContract, s)
	if err != nil {
		return out, fmt.Errorf("bad contract strkey: %w", err)
	}
	copy(out[:], raw)
	return out, nil
}

func idFromHex(s string) ([32]byte, error) {
	var out [32]byte
	raw, err := hex.DecodeString(s)
	if err != nil || len(raw) != 32 {
		return out, fmt.Errorf("event id must be 32-byte hex")
	}
	copy(out[:], raw)
	return out, nil
}

// --- value decoding (ScVal -> domain) ---

func decodeBytesVec(v xdr.ScVal) ([]string, error) {
	if v.Vec == nil || *v.Vec == nil {
		return []string{}, nil
	}
	out := []string{}
	for _, item := range **v.Vec {
		if item.Bytes == nil {
			return nil, fmt.Errorf("expected bytes in vec")
		}
		out = append(out, hex.EncodeToString([]byte(*item.Bytes)))
	}
	return out, nil
}

func decodeAddressVec(v xdr.ScVal) ([]string, error) {
	if v.Vec == nil || *v.Vec == nil {
		return []string{}, nil
	}
	out := []string{}
	for _, item := range **v.Vec {
		if item.Address == nil {
			return nil, fmt.Errorf("expected address in vec")
		}
		s, err := item.Address.String()
		if err != nil {
			return nil, err
		}
		out = append(out, s)
	}
	return out, nil
}

func decodeEventMetadata(v xdr.ScVal) (EventMetadata, error) {
	var m EventMetadata
	if v.Map == nil || *v.Map == nil {
		return m, fmt.Errorf("expected map")
	}
	for _, entry := range **v.Map {
		if entry.Key.Sym == nil || entry.Val.Str == nil {
			continue
		}
		val := string(*entry.Val.Str)
		switch string(*entry.Key.Sym) {
		case "name":
			m.Name = val
		case "description":
			m.Description = val
		case "image_ipfs":
			m.ImageIpfs = val
		}
	}
	return m, nil
}
