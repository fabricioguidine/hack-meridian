package main

import (
	"encoding/json"
	"net/http"
	"strings"
)

type Server struct {
	reader Reader
}

func NewServer(r Reader) *Server { return &Server{reader: r} }

func (s *Server) Routes() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	mux.HandleFunc("/events", s.handleEvents)
	mux.HandleFunc("/gallery", s.handleGallery)
	mux.HandleFunc("/events/", s.handleEventByID)
	mux.HandleFunc("/users/", s.handleUserBadges)
	return mux
}

func (s *Server) handleEvents(w http.ResponseWriter, _ *http.Request) {
	ids, err := s.reader.ListEvents()
	if err != nil {
		writeErr(w, http.StatusBadGateway, err)
		return
	}
	writeJSON(w, http.StatusOK, ids)
}

func (s *Server) handleGallery(w http.ResponseWriter, _ *http.Request) {
	ids, err := s.reader.ListEvents()
	if err != nil {
		writeErr(w, http.StatusBadGateway, err)
		return
	}
	events := []Event{}
	for _, id := range ids {
		meta, err := s.reader.GetEvent(id)
		if err != nil || meta == nil {
			continue
		}
		events = append(events, Event{Id: id, EventMetadata: *meta})
	}
	writeJSON(w, http.StatusOK, events)
}

// /events/:id  and  /events/:id/owners
func (s *Server) handleEventByID(w http.ResponseWriter, r *http.Request) {
	rest := strings.TrimPrefix(r.URL.Path, "/events/")
	if rest == "" {
		writeErr(w, http.StatusBadRequest, errString("missing event id"))
		return
	}
	if strings.HasSuffix(rest, "/owners") {
		id := strings.TrimSuffix(rest, "/owners")
		owners, err := s.reader.EventOwners(id)
		if err != nil {
			writeErr(w, http.StatusBadGateway, err)
			return
		}
		writeJSON(w, http.StatusOK, owners)
		return
	}
	meta, err := s.reader.GetEvent(rest)
	if err != nil {
		writeErr(w, http.StatusBadGateway, err)
		return
	}
	if meta == nil {
		writeErr(w, http.StatusNotFound, errString("not found"))
		return
	}
	writeJSON(w, http.StatusOK, Event{Id: rest, EventMetadata: *meta})
}

// /users/:account/badges
func (s *Server) handleUserBadges(w http.ResponseWriter, r *http.Request) {
	rest := strings.TrimPrefix(r.URL.Path, "/users/")
	account := strings.TrimSuffix(rest, "/badges")
	if account == "" || account == rest {
		writeErr(w, http.StatusBadRequest, errString("expected /users/:account/badges"))
		return
	}
	ids, err := s.reader.UserBadges(account)
	if err != nil {
		writeErr(w, http.StatusBadGateway, err)
		return
	}
	writeJSON(w, http.StatusOK, ids)
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func writeErr(w http.ResponseWriter, status int, err error) {
	writeJSON(w, status, map[string]string{"error": err.Error()})
}

type errString string

func (e errString) Error() string { return string(e) }
