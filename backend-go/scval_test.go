package main

import (
	"encoding/hex"
	"strings"
	"testing"

	"github.com/stellar/go/strkey"
	"github.com/stellar/go/xdr"
)

func scString(s string) xdr.ScVal {
	v := xdr.ScString(s)
	return xdr.ScVal{Type: xdr.ScValTypeScvString, Str: &v}
}

func scMap(entries []xdr.ScMapEntry) xdr.ScVal {
	m := xdr.ScMap(entries)
	pm := &m
	return xdr.ScVal{Type: xdr.ScValTypeScvMap, Map: &pm}
}

func TestIdFromHexRoundtrip(t *testing.T) {
	var id [32]byte
	for i := range id {
		id[i] = 7
	}
	h := hex.EncodeToString(id[:])
	got, err := idFromHex(h)
	if err != nil || got != id {
		t.Fatalf("roundtrip failed: %v", err)
	}
	if _, err := idFromHex("abcd"); err == nil {
		t.Fatal("short hex should fail")
	}
}

func TestLedgerKeyEncodes(t *testing.T) {
	var c [32]byte
	c[0] = 1
	b64, err := ledgerKeyB64(c, keyEvents())
	if err != nil || b64 == "" {
		t.Fatalf("ledger key encode failed: %v", err)
	}
	if _, err := ledgerKeyB64(c, keyEventMeta([32]byte{2})); err != nil {
		t.Fatal(err)
	}
}

func TestDecodeBytesVec(t *testing.T) {
	var a, b [32]byte
	for i := range a {
		a[i] = 0xaa
		b[i] = 0xbb
	}
	v := scVec(bytes32(a), bytes32(b))
	out, err := decodeBytesVec(v)
	if err != nil || len(out) != 2 {
		t.Fatalf("got %v err %v", out, err)
	}
	if out[0] != strings.Repeat("aa", 32) || out[1] != strings.Repeat("bb", 32) {
		t.Fatalf("unexpected: %v", out)
	}
}

func TestDecodeEmptyVec(t *testing.T) {
	out, err := decodeBytesVec(xdr.ScVal{Type: xdr.ScValTypeScvVec})
	if err != nil || len(out) != 0 {
		t.Fatalf("expected empty, got %v err %v", out, err)
	}
}

func TestDecodeEventMetadata(t *testing.T) {
	m := scMap([]xdr.ScMapEntry{
		{Key: symbol("name"), Val: scString("Meridian 2025")},
		{Key: symbol("description"), Val: scString("Attended")},
		{Key: symbol("image_ipfs"), Val: scString("ipfs://Qm")},
	})
	meta, err := decodeEventMetadata(m)
	if err != nil {
		t.Fatal(err)
	}
	if meta.Name != "Meridian 2025" || meta.ImageIpfs != "ipfs://Qm" {
		t.Fatalf("unexpected: %+v", meta)
	}
}

func TestDecodeAddressVec(t *testing.T) {
	zero, err := strkey.Encode(strkey.VersionByteAccountID, make([]byte, 32))
	if err != nil {
		t.Fatal(err)
	}
	aid, err := xdr.AddressToAccountId(zero)
	if err != nil {
		t.Fatal(err)
	}
	addr := xdr.ScAddress{Type: xdr.ScAddressTypeScAddressTypeAccount, AccountId: &aid}
	av := xdr.ScVal{Type: xdr.ScValTypeScvAddress, Address: &addr}
	out, err := decodeAddressVec(scVec(av))
	if err != nil || len(out) != 1 {
		t.Fatalf("got %v err %v", out, err)
	}
	if out[0] != zero {
		t.Fatalf("expected %s got %s", zero, out[0])
	}
}
