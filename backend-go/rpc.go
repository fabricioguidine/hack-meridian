package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/stellar/go/xdr"
)

// Reader reads poap_badge state. Implemented by RpcClient; mocked in tests.
type Reader interface {
	ListEvents() ([]string, error)
	GetEvent(idHex string) (*EventMetadata, error)
	EventOwners(idHex string) ([]string, error)
	UserBadges(account string) ([]string, error)
}

type RpcClient struct {
	url      string
	contract [32]byte
	http     *http.Client
}

func NewRpcClient(url, contractID string) (*RpcClient, error) {
	cid, err := contractIdFromStrkey(contractID)
	if err != nil {
		return nil, err
	}
	return &RpcClient{url: url, contract: cid, http: &http.Client{Timeout: 20 * time.Second}}, nil
}

type rpcReq struct {
	JsonRPC string         `json:"jsonrpc"`
	Id      int            `json:"id"`
	Method  string         `json:"method"`
	Params  map[string]any `json:"params"`
}

type rpcResp struct {
	Result *struct {
		Entries []struct {
			Xdr string `json:"xdr"`
		} `json:"entries"`
	} `json:"result"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error"`
}

// fetchValue returns the stored ScVal for a key, or nil if the entry is absent.
func (c *RpcClient) fetchValue(key xdr.ScVal) (*xdr.ScVal, error) {
	keyB64, err := ledgerKeyB64(c.contract, key)
	if err != nil {
		return nil, err
	}
	body, _ := json.Marshal(rpcReq{
		JsonRPC: "2.0",
		Id:      1,
		Method:  "getLedgerEntries",
		Params:  map[string]any{"keys": []string{keyB64}},
	})
	resp, err := c.http.Post(c.url, "application/json", bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("rpc: %w", err)
	}
	defer resp.Body.Close()

	var parsed rpcResp
	if err := json.NewDecoder(resp.Body).Decode(&parsed); err != nil {
		return nil, fmt.Errorf("rpc decode: %w", err)
	}
	if parsed.Error != nil {
		return nil, fmt.Errorf("rpc error: %s", parsed.Error.Message)
	}
	if parsed.Result == nil || len(parsed.Result.Entries) == 0 {
		return nil, nil
	}
	var data xdr.LedgerEntryData
	if err := xdr.SafeUnmarshalBase64(parsed.Result.Entries[0].Xdr, &data); err != nil {
		return nil, fmt.Errorf("entry xdr: %w", err)
	}
	if data.ContractData == nil {
		return nil, fmt.Errorf("not contract data")
	}
	val := data.ContractData.Val
	return &val, nil
}

func (c *RpcClient) ListEvents() ([]string, error) {
	v, err := c.fetchValue(keyEvents())
	if err != nil || v == nil {
		return []string{}, err
	}
	return decodeBytesVec(*v)
}

func (c *RpcClient) GetEvent(idHex string) (*EventMetadata, error) {
	id, err := idFromHex(idHex)
	if err != nil {
		return nil, err
	}
	v, err := c.fetchValue(keyEventMeta(id))
	if err != nil {
		return nil, err
	}
	if v == nil {
		return nil, nil
	}
	m, err := decodeEventMetadata(*v)
	if err != nil {
		return nil, err
	}
	return &m, nil
}

func (c *RpcClient) EventOwners(idHex string) ([]string, error) {
	id, err := idFromHex(idHex)
	if err != nil {
		return nil, err
	}
	v, err := c.fetchValue(keyEventOwners(id))
	if err != nil || v == nil {
		return []string{}, err
	}
	return decodeAddressVec(*v)
}

func (c *RpcClient) UserBadges(account string) ([]string, error) {
	key, err := keyUserBadges(account)
	if err != nil {
		return nil, err
	}
	v, err := c.fetchValue(key)
	if err != nil || v == nil {
		return []string{}, err
	}
	return decodeBytesVec(*v)
}
