/// Sanitize a topic name to lowerCamelCase (for GraphQL query fields).
pub fn sanitize_to_graphql_name(raw: &str) -> String {
    to_camel_case(raw)
}

/// Convert a raw identifier to lowerCamelCase.
///
/// Tokens are split on every non-alphanumeric character, so `a/b-c` and
/// `a_b_c` both become `aBC`. A leading digit is prefixed with `_` to keep
/// the result a valid GraphQL name, and an underscore is inserted between two
/// adjacent digit-only tokens (`string1-2` → `string1_2`) so that `string1-2`
/// and `string12` cannot collide after sanitization.
fn to_camel_case(raw: &str) -> String {
    let parts = split_to_words(raw);
    if parts.is_empty() {
        return String::new();
    }
    let mut out = String::new();
    for (i, part) in parts.iter().enumerate() {
        let is_digits = part.chars().all(|c| c.is_ascii_digit());
        let prev_ends_digit = out.chars().last().is_some_and(|c| c.is_ascii_digit());
        // Preserve boundary between digit-only parts (e.g. "string1-2" vs "string12")
        if is_digits && prev_ends_digit {
            out.push('_');
            out.push_str(part);
            continue;
        }
        if i == 0 {
            out.push_str(&part.to_ascii_lowercase());
        } else {
            let mut chars = part.chars();
            if let Some(first) = chars.next() {
                out.push(first.to_ascii_uppercase());
                out.push_str(&chars.as_str().to_ascii_lowercase());
            }
        }
    }
    if out.chars().next().is_some_and(|c| c.is_ascii_digit()) {
        out.insert(0, '_');
    }
    out
}

fn split_to_words(raw: &str) -> Vec<String> {
    let mut words: Vec<String> = Vec::new();
    let mut current = String::new();
    for c in raw.chars() {
        if c.is_alphanumeric() {
            current.push(c);
        } else if !current.is_empty() {
            words.push(std::mem::take(&mut current));
        }
    }
    if !current.is_empty() {
        words.push(current);
    }
    words
}

/// PascalCase form of a group id (`power-tags` → `PowerTags`).
pub fn pascal_case(name: &str) -> String {
    let camel = sanitize_to_graphql_name(name);
    let mut chars = camel.chars();
    match chars.next() {
        Some(first) => first.to_ascii_uppercase().to_string() + chars.as_str(),
        None => String::new(),
    }
}

/// Reserved GraphQL names that cannot be used for topic query fields (lowerCamelCase).
const RESERVED_GRAPHQL_NAMES: &[&str] = &[
    "query",
    "mutation",
    "subscription",
    "topics",
    "boolean",
    "float",
    "int",
    "string",
    "id",
];

/// Whether `name` collides with a reserved GraphQL name.
pub fn is_reserved_name(name: &str) -> bool {
    RESERVED_GRAPHQL_NAMES.contains(&name)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sanitize_slashes() {
        assert_eq!(sanitize_to_graphql_name("a/b/c"), "aBC");
    }

    #[test]
    fn test_sanitize_dashes() {
        assert_eq!(sanitize_to_graphql_name("my-topic"), "myTopic");
    }

    #[test]
    fn test_sanitize_digit_prefix() {
        assert_eq!(sanitize_to_graphql_name("123abc"), "_123abc");
    }

    #[test]
    fn test_sanitize_underscore_collapse() {
        assert_eq!(sanitize_to_graphql_name("a/-b"), "aB");
    }

    #[test]
    fn test_sanitize_camel_case_topic() {
        assert_eq!(
            sanitize_to_graphql_name("termodinamica/compressor/temperature"),
            "termodinamicaCompressorTemperature"
        );
        assert_eq!(
            sanitize_to_graphql_name("power-tags/10P1/ahu1500-aft-area"),
            "powerTags10p1Ahu1500AftArea"
        );
        assert_eq!(
            sanitize_to_graphql_name("hull-temperature/temperatures"),
            "hullTemperatureTemperatures"
        );
        assert_eq!(sanitize_to_graphql_name("my_field_name"), "myFieldName");
        assert_eq!(sanitize_to_graphql_name("94455001-26"), "_94455001_26");
    }

    #[test]
    fn test_sanitize_empty_and_single_word() {
        assert_eq!(sanitize_to_graphql_name(""), "");
        assert_eq!(sanitize_to_graphql_name("---"), "");
        assert_eq!(sanitize_to_graphql_name("hello"), "hello");
        assert_eq!(sanitize_to_graphql_name("Hello"), "hello");
    }

    #[test]
    fn test_pascal_case() {
        assert_eq!(pascal_case("power-tags"), "PowerTags");
        assert_eq!(pascal_case(""), "");
    }
}
