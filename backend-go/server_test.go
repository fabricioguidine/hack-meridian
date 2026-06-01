package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

type mockReader struct{}

func (mockReader) ListEvents() ([]string, error) {
	return []string{strings.Repeat("aa", 32)}, nil
}

func (mockReader) GetEvent(id string) (*EventMetadata, error) {
	if id == strings.Repeat("ff", 32) {
		return nil, nil
	}
	return &EventMetadata{Name: "Meridian 2025", Description: "d", ImageIpfs: "ipfs://Q"}, nil
}

func (mockReader) EventOwners(string) ([]string, error) { return []string{"GABC"}, nil }
func (mockReader) UserBadges(string) ([]string, error) {
	return []string{strings.Repeat("aa", 32)}, nil
}

func do(t *testing.T, path string) *httptest.ResponseRecorder {
	t.Helper()
	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, path, nil)
	NewServer(mockReader{}).Routes().ServeHTTP(rec, req)
	return rec
}

func TestGallery(t *testing.T) {
	rec := do(t, "/gallery")
	if rec.Code != 200 {
		t.Fatalf("status %d", rec.Code)
	}
	var events []Event
	if err := json.Unmarshal(rec.Body.Bytes(), &events); err != nil {
		t.Fatal(err)
	}
	if len(events) != 1 || events[0].Name != "Meridian 2025" {
		t.Fatalf("unexpected: %+v", events)
	}
}

func TestEventByID(t *testing.T) {
	rec := do(t, "/events/"+strings.Repeat("aa", 32))
	if rec.Code != 200 {
		t.Fatalf("status %d", rec.Code)
	}
	var ev Event
	if err := json.Unmarshal(rec.Body.Bytes(), &ev); err != nil {
		t.Fatal(err)
	}
	if ev.Id != strings.Repeat("aa", 32) {
		t.Fatalf("unexpected id: %s", ev.Id)
	}
}

func TestEventNotFound(t *testing.T) {
	rec := do(t, "/events/"+strings.Repeat("ff", 32))
	if rec.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", rec.Code)
	}
}

func TestEventOwners(t *testing.T) {
	rec := do(t, "/events/"+strings.Repeat("aa", 32)+"/owners")
	if rec.Code != 200 {
		t.Fatalf("status %d", rec.Code)
	}
	var owners []string
	if err := json.Unmarshal(rec.Body.Bytes(), &owners); err != nil {
		t.Fatal(err)
	}
	if len(owners) != 1 || owners[0] != "GABC" {
		t.Fatalf("unexpected: %v", owners)
	}
}

func TestUserBadges(t *testing.T) {
	rec := do(t, "/users/GABC/badges")
	if rec.Code != 200 {
		t.Fatalf("status %d", rec.Code)
	}
}
