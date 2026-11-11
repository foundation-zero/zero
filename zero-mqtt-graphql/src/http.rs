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

/// URLs the async-graphql GraphiQL page leaves unpinned, pinned to match its
/// `graphiql@5.2.2`; esm.sh would otherwise serve the latest of each, such as
/// the stylesheet of graphiql 6.
const GRAPHIQL_PINS: [(&str, &str); 5] = [
    (
        "esm.sh/graphiql/dist/style.css",
        "esm.sh/graphiql@5.2.2/dist/style.css",
    ),
    (
        "esm.sh/@graphiql/plugin-explorer/dist/style.css",
        "esm.sh/@graphiql/plugin-explorer@5.1.3/dist/style.css",
    ),
    ("esm.sh/@graphiql/react?", "esm.sh/@graphiql/react@0.37.7?"),
    (
        "esm.sh/@graphiql/plugin-explorer?",
        "esm.sh/@graphiql/plugin-explorer@5.1.3?",
    ),
    // `@graphiql/react` 0.37 needs toolkit `^0.12.1`.
    (
        "esm.sh/@graphiql/toolkit?",
        "esm.sh/@graphiql/toolkit@0.12.1?",
    ),
];

async fn graphql_playground() -> Html<String> {
    let page = GraphiQLSource::build().endpoint("/graphql").finish();
    Html(
        GRAPHIQL_PINS
            .iter()
            .fold(page, |page, (from, to)| page.replace(from, to)),
    )
}

/// Liveness probe. Deliberately does not touch the MQTT connection: a
/// temporarily disconnected broker should not fail readiness here.
async fn health() -> &'static str {
    "OK"
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::http::router;
    use async_graphql::dynamic::{Field, FieldFuture, Object, TypeRef};
    use axum::http::StatusCode;
    use tower::ServiceExt;

    #[tokio::test]
    #[test_log::test]
    async fn test_health_endpoint() {
        let basic_schema = Schema::build("query", None, None)
            .register(Object::new("query").field(Field::new(
                "test",
                TypeRef::named(TypeRef::BOOLEAN),
                |_| FieldFuture::from_value(None),
            )))
            .finish()
            .unwrap();
        let app = router(basic_schema);

        let response = app
            .oneshot(
                axum::http::Request::builder()
                    .uri("/health")
                    .body(axum::body::Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);
    }

    /// The package an esm.sh URL loads, with its version if it has one:
    /// `@graphiql/react@0.37.7` for
    /// `@graphiql/react@0.37.7?standalone&external=react`.
    fn esm_package(url_path: &str) -> String {
        let end = url_path.find(['?', '"', '\'']).unwrap_or(url_path.len());
        // A scoped package spans two path segments.
        let segments = if url_path.starts_with('@') { 2 } else { 1 };
        url_path[..end]
            .split('/')
            .take(segments)
            .collect::<Vec<_>>()
            .join("/")
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_playground_pins_every_esm_sh_package() {
        let Html(page) = graphql_playground().await;

        let unpinned: Vec<String> = page
            .split("https://esm.sh/")
            .skip(1)
            .map(esm_package)
            .filter(|package| !package.trim_start_matches('@').contains('@'))
            .collect();
        assert!(
            unpinned.is_empty(),
            "unpinned esm.sh packages: {unpinned:?}"
        );
    }
}
