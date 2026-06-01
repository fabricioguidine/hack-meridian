package main

// EventMetadata mirrors the contract's EventMetadata.
type EventMetadata struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	ImageIpfs   string `json:"image_ipfs"`
}

// Event is an event id (hex) plus its metadata (flattened in JSON).
type Event struct {
	Id string `json:"id"`
	EventMetadata
}
