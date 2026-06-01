mod config;
mod domain;
mod error;
mod routes;
mod soroban;

use std::sync::Arc;

use tower_http::{cors::CorsLayer, trace::TraceLayer};

use crate::config::Config;
use crate::routes::AppState;
use crate::soroban::rpc::RpcClient;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()),
        )
        .init();

    let cfg = Config::from_env().expect("invalid configuration");
    let reader = RpcClient::new(cfg.rpc_url.clone(), &cfg.contract_id).expect("rpc client");
    let state = AppState {
        reader: Arc::new(reader),
    };

    let app = routes::router(state)
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http());

    let addr = format!("0.0.0.0:{}", cfg.port);
    tracing::info!("poap_badge_api listening on {addr}");
    let listener = tokio::net::TcpListener::bind(&addr)
        .await
        .expect("bind address");
    axum::serve(listener, app).await.expect("server error");
}
