use std::sync::LazyLock;

use convert_case::{Boundary, Case, Casing, Converter, Pattern};

static INVALID_CHARS: Boundary = Boundary::Custom {
    condition: |s: &[&str]| {
        s.first()
            .and_then(|g| g.chars().take(1).map(|c: char| !c.is_alphanumeric()).next())
            .unwrap_or(false)
    },
    start: 0,
    len: 1,
};

/// Applies capital pattern to a single word using graphemes.
fn capital_word(word: &str) -> String {
    let mut chars = word.chars();

    if let Some(c) = chars.next() {
        [
            c.to_uppercase().collect(),
            chars.as_str().to_ascii_lowercase(),
        ]
        .concat()
    } else {
        String::new()
    }
}

/// camel-case-1-2 -> camelCase1_2
static CAMEL_WITH_DIGIT_GROUPS: Pattern = Pattern::Custom(|words| {
    words
        .iter()
        .enumerate()
        .fold(Vec::with_capacity(words.len()), |mut acc, (i, word)| {
            let word = if i == 0 {
                word.to_ascii_lowercase()
            } else {
                capital_word(word)
            };

            // Fix digit groups
            if let Some(prev) = acc.last_mut()
                && prev.ends_with(|c: char| c.is_ascii_digit())
                && word.starts_with(|c: char| c.is_ascii_digit())
            {
                prev.push('_');
            }

            acc.push(word);
            acc
        })
});

// Basically CamelCase but we skip anything that is not alphanumeric and it keeps an extra '-' as separator for digit groups
static GRAPHQL_CASE_CONVERTER: LazyLock<Converter> = LazyLock::new(|| {
    Converter::new()
        .set_boundaries(&[
            INVALID_CHARS,
            Boundary::LowerUpper,
            Boundary::Acronym,
            Boundary::DigitLower,
            Boundary::DigitUpper,
        ])
        .set_pattern(CAMEL_WITH_DIGIT_GROUPS)
        .set_delimiter("")
});

/// Sanitize a topic name to lowerCamelCase and other stuff for GraphQL query fields.
#[must_use]
pub fn sanitize_to_graphql_name(raw: &str) -> String {
    let mut result = GRAPHQL_CASE_CONVERTER.convert(raw);

    // Make sure we don't start with a digit
    if result.starts_with(|c: char| c.is_ascii_digit()) {
        result.insert(0, '_');
    }

    result
}

/// PascalCase form of a sanitized graphql name (`power-tags` → `PowerTags`).
#[must_use]
pub fn pascal_case_graphql_name(name: &str) -> String {
    let camel = sanitize_to_graphql_name(name);
    let mut chars = camel.chars();
    match chars.next() {
        Some(first) => first.to_ascii_uppercase().to_string() + chars.as_str(),
        None => String::new(),
    }
}

/// The GraphQL name of an enum value, in `SCREAMING_SNAKE_CASE`
/// (`needs boost` → `NEEDS_BOOST`); `None` when it has no valid one, such as
/// one starting with `__`, which GraphQL reserves for introspection.
#[must_use]
pub fn enum_value_name(raw: &str) -> Option<String> {
    let mut name = raw.to_case(Case::Constant);
    if name.starts_with(|c: char| c.is_ascii_digit()) {
        name.insert(0, '_');
    }
    let valid = !name.is_empty()
        && !name.starts_with("__")
        && name
            .chars()
            .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '_');
    valid.then_some(name)
}

/// Reserved GraphQL names that cannot be used for topic query fields (lowerCamelCase).
const RESERVED_GRAPHQL_NAMES: &[&str] = &[
    "query",
    "mutation",
    "subscription",
    "boolean",
    "float",
    "int",
    "string",
    "id",
];

/// Whether `name` collides with a reserved GraphQL name.
#[must_use]
pub fn is_reserved_name(name: &str) -> bool {
    RESERVED_GRAPHQL_NAMES.contains(&name.to_ascii_lowercase().as_ref())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test_log::test]
    fn test_sanitize_slashes() {
        assert_eq!(sanitize_to_graphql_name("a/b/c"), "aBC");
    }

    #[test_log::test]
    fn test_sanitize_dashes() {
        assert_eq!(sanitize_to_graphql_name("my-topic"), "myTopic");
    }

    #[test_log::test]
    fn test_sanitize_digit_prefix() {
        assert_eq!(sanitize_to_graphql_name("123abc"), "_123Abc");
    }

    #[test_log::test]
    fn test_sanitize_underscore_collapse() {
        assert_eq!(sanitize_to_graphql_name("a/-b"), "aB");
    }

    #[test_log::test]
    fn test_sanitize_camel_case_topic() {
        assert_eq!(
            sanitize_to_graphql_name("termodinamica/compressor/temperature"),
            "termodinamicaCompressorTemperature"
        );
        assert_eq!(
            sanitize_to_graphql_name("power-tags/10P1/ahu1500-aft-area"),
            "powerTags10P1Ahu1500AftArea"
        );
        assert_eq!(
            sanitize_to_graphql_name("hull-temperature/temperatures"),
            "hullTemperatureTemperatures"
        );
        assert_eq!(sanitize_to_graphql_name("my_field_name"), "myFieldName");
        assert_eq!(sanitize_to_graphql_name("94455001-26"), "_94455001_26");
    }

    #[test_log::test]
    fn test_sanitize_empty_and_single_word() {
        assert_eq!(sanitize_to_graphql_name(""), "");
        assert_eq!(sanitize_to_graphql_name("---"), "");
        assert_eq!(sanitize_to_graphql_name("hello"), "hello");
        assert_eq!(sanitize_to_graphql_name("Hello"), "hello");
    }

    #[test_log::test]
    fn test_pascal_case() {
        assert_eq!(pascal_case_graphql_name("power-tags"), "PowerTags");
        assert_eq!(pascal_case_graphql_name(""), "");
    }

    #[test_log::test]
    fn test_is_reserved_name() {
        assert!(!is_reserved_name("power-tags"));

        assert!(
            &[
                "query",
                "mutation",
                "subscription",
                "boolean",
                "float",
                "int",
                "string",
                "id",
            ]
            .iter()
            .all(|n| is_reserved_name(n))
        );
    }

    #[test_log::test]
    fn test_enum_value_name() {
        for (raw, name) in [
            ("propulsion", "PROPULSION"),
            ("in use", "IN_USE"),
            ("needs-boost", "NEEDS_BOOST"),
            ("valveRun", "VALVE_RUN"),
            ("1st", "_1_ST"),
        ] {
            assert_eq!(enum_value_name(raw).as_deref(), Some(name), "for {raw}");
        }
        for raw in ["", "a.b", "é", "__schema", "__"] {
            assert_eq!(enum_value_name(raw), None, "for {raw}");
        }
    }
}
