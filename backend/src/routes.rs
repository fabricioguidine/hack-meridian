use std::sync::Arc;

use axum::{
    extract::{Path, State},
    routing::get,
    Json, Router,
};
use serde_json::json;

use crate::domain::Event;
use crate::error::AppError;
use crate::soroban::SorobanReader;

#[derive(Clone)]
pub struct AppState {
    pub reader: Arc<dyn SorobanReader>,
}

pub fn router(state: AppState) -> Router {
    Router::new()
        .route("/health", get(health))
        .route("/events", get(list_events))
        .route("/events/:id", get(get_event))
        .route("/events/:id/owners", get(event_owners))
        .route("/users/:account/badges", get(user_badges))
        .route("/gallery", get(gallery))
        .with_state(state)
}

async fn health() -> Json<serde_json::Value> {
    Json(json!({ "status": "ok" }))
}

async fn list_events(State(s): State<AppState>) -> Result<Json<Vec<String>>, AppError> {
    Ok(Json(s.reader.list_events().await?))
}

async fn get_event(
    State(s): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<Event>, AppError> {
    let metadata = s.reader.get_event(&id).await?;
    Ok(Json(Event { id, metadata }))
}

async fn event_owners(
    State(s): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<Vec<String>>, AppError> {
    Ok(Json(s.reader.event_owners(&id).await?))
}

async fn user_badges(
    State(s): State<AppState>,
    Path(account): Path<String>,
) -> Result<Json<Vec<String>>, AppError> {
    Ok(Json(s.reader.user_badges(&account).await?))
}

async fn gallery(State(s): State<AppState>) -> Result<Json<Vec<Event>>, AppError> {
    let ids = s.reader.list_events().await?;
    let mut events = Vec::with_capacity(ids.len());
    for id in ids {
        let metadata = s.reader.get_event(&id).await?;
        events.push(Event { id, metadata });
    }
    Ok(Json(events))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::EventMetadata;
    use async_trait::async_trait;

    struct Mock;

    #[async_trait]
    impl SorobanReader for Mock {
        async fn list_events(&self) -> Result<Vec<String>, AppError> {
            Ok(vec!["aa".repeat(32)])
        }
        async fn get_event(&self, id_hex: &str) -> Result<EventMetadata, AppError> {
            if id_hex == "ff".repeat(32) {
                return Err(AppError::NotFound);
            }
            Ok(EventMetadata {
                name: "Meridian 2025".into(),
                description: "demo".into(),
                image_ipfs: "ipfs://Qm".into(),
            })
        }
        async fn event_owners(&self, _id_hex: &str) -> Result<Vec<String>, AppError> {
            Ok(vec!["GABC".into()])
        }
        async fn user_badges(&self, _account: &str) -> Result<Vec<String>, AppError> {
            Ok(vec!["aa".repeat(32)])
        }
    }

    fn state() -> AppState {
        AppState {
            reader: Arc::new(Mock),
        }
    }

    #[tokio::test]
    async fn list_events_ok() {
        let Json(ids) = list_events(State(state())).await.unwrap();
        assert_eq!(ids.len(), 1);
    }

    #[tokio::test]
    async fn get_event_ok() {
        let Json(ev) = get_event(State(state()), Path("aa".repeat(32)))
            .await
            .unwrap();
        assert_eq!(ev.metadata.name, "Meridian 2025");
        assert_eq!(ev.id, "aa".repeat(32));
    }

    #[tokio::test]
    async fn get_event_missing_is_not_found() {
        let err = get_event(State(state()), Path("ff".repeat(32)))
            .await
            .unwrap_err();
        assert!(matches!(err, AppError::NotFound));
    }

    #[tokio::test]
    async fn gallery_composes_events() {
        let Json(events) = gallery(State(state())).await.unwrap();
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].metadata.image_ipfs, "ipfs://Qm");
    }
}
