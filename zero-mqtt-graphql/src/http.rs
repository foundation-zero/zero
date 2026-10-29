use async_graphql::{dynamic::Schema, http::GraphiQLSource};
use axum::{
    Json, Router,
    extract::Extension,
    http::StatusCode,
    response::Html,
    routing::{get, post},
};
use log::warn;
use tower_http::cors::{Any, CorsLayer};

/// Build the axum Router for HTTP endpoints.
pub fn router(schema: Schema) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any)
        .expose_headers(Any);

    Router::new()
        .route("/", get(graphql_playground))
        .route("/graphql", post(graphql_handler))
        .route("/health", get(health))
        .layer(cors)
        .layer(Extension(schema))
}

async fn graphql_handler(
    Extension(schema): Extension<Schema>,
    Json(request): Json<async_graphql::Request>,
) -> Result<Json<async_graphql::Response>, StatusCode> {
    let response = schema.execute(request).await;
    if response.is_ok() {
        Ok(Json(response))
    } else {
        warn!("GraphQL errors: {:?}", response.errors);
        Ok(Json(response))
    }
}

async fn graphql_playground() -> Html<String> {
    Html(GraphiQLSource::build().endpoint("/graphql").finish())
}

/// Liveness probe. Deliberately does not touch the MQTT connection: a
/// temporarily disconnected broker should not fail readiness here.
async fn health() -> &'static str {
    "OK"
}
