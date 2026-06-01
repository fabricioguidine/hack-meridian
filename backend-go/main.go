package main

import (
	"log"
	"net/http"
	"os"
)

func main() {
	rpcURL := getenv("SOROBAN_RPC_URL", "https://soroban-testnet.stellar.org")
	contractID := os.Getenv("CONTRACT_ID")
	port := getenv("PORT", "4001")

	if contractID == "" {
		log.Fatal("CONTRACT_ID is required (deployed C... strkey)")
	}
	client, err := NewRpcClient(rpcURL, contractID)
	if err != nil {
		log.Fatalf("rpc client: %v", err)
	}

	srv := NewServer(client)
	log.Printf("poap_badge_api (go) listening on :%s", port)
	if err := http.ListenAndServe(":"+port, srv.Routes()); err != nil {
		log.Fatal(err)
	}
}

func getenv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
