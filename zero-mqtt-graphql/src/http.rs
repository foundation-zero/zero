use async_graphql::dynamic::Schema;
use axum::{
    extract::Extension,
    http::StatusCode,
    response::Html,
    routing::{get, post},
    Json, Router,
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
        .route("/graphql", post(graphql_handler).get(graphql_playground))
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
    Html(async_graphql::http::playground_source(
        async_graphql::http::GraphQLPlaygroundConfig::new("/graphql"),
    ))
}

/// Liveness probe. Deliberately does not touch the MQTT connection: a
/// temporarily disconnected broker should not fail readiness here.
async fn health() -> &'static str {
    "OK"
}
