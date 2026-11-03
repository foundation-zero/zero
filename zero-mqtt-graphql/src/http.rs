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
    if response.is_err() {
        warn!("GraphQL errors: {:?}", response.errors);
    }
    Ok(Json(response))
}

async fn graphql_playground() -> Html<String> {
    Html(
        GraphiQLSource::build()
            .endpoint("/graphql")
            .finish()
            // Workaround for missing pin
            .replace("esm.sh/@graphiql/react?", "esm.sh/@graphiql/react@0.37.7?")
            .replace(
                "esm.sh/@graphiql/plugin-explorer?",
                "esm.sh/@graphiql/plugin-explorer@5.1.3?",
            ),
    )
}

/// Liveness probe. Deliberately does not touch the MQTT connection: a
/// temporarily disconnected broker should not fail readiness here.
async fn health() -> &'static str {
    "OK"
}
