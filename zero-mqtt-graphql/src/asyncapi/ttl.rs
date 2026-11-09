//! Cache TTLs from `x-ttl` extensions.

use std::collections::BTreeMap;

use log::warn;
use serde_json::Value;

use super::roas::{Channel, Document};
use super::schema::channel_messages;

/// Effective TTL for cached values of a channel: the maximum `x-ttl`
/// across its messages (a channel may declare several), falling back to the
/// channel's own extension, then the global default.
pub(super) fn ttl_for_channel(channel_ref: &str, channel: &Channel, doc: &Document) -> Option<u64> {
    channel_messages(channel_ref, channel, doc)
        .into_values()
        .filter_map(|message| ttl_from_extensions(message.extensions.as_ref()))
        .max()
        .or_else(|| ttl_from_extensions(channel.extensions.as_ref()))
}

fn ttl_from_extensions(ext: Option<&BTreeMap<String, Value>>) -> Option<u64> {
    let map = ext?;
    ttl_from_value(map.get("x-ttl"))
}

fn ttl_from_value(v: Option<&Value>) -> Option<u64> {
    match v? {
        Value::Number(n) => n.as_u64(),
        Value::String(s) => parse_ttl_str(s),
        _ => None,
    }
}

/// Parse an `x-ttl` string: plain seconds (`"300"`) or a suffixed form
/// (`"30s"`, `"5m"`, `"1h"`). Logs and returns `None` on unsupported values.
fn parse_ttl_str(s: &str) -> Option<u64> {
    if let Ok(n) = s.parse::<u64>() {
        return Some(n);
    }
    let (num, mult) = if let Some(num) = s.strip_suffix('h') {
        (num, 3600)
    } else if let Some(num) = s.strip_suffix('m') {
        (num, 60)
    } else if let Some(num) = s.strip_suffix('s') {
        (num, 1)
    } else {
        warn!(
            "Unsupported x-ttl value '{s}' (expected seconds, '30s', '5m' or '1h') — using default"
        );
        return None;
    };
    if let Ok(n) = num.parse::<u64>() {
        Some(n * mult)
    } else {
        warn!(
            "Unparseable x-ttl value '{s}' (expected seconds, '30s', '5m' or '1h') — using default"
        );
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test_log::test]
    fn test_parse_ttl_str() {
        assert_eq!(parse_ttl_str("300"), Some(300));
        assert_eq!(parse_ttl_str("30s"), Some(30));
        assert_eq!(parse_ttl_str("5m"), Some(300));
        assert_eq!(parse_ttl_str("1h"), Some(3600));
        assert_eq!(parse_ttl_str("0"), Some(0));
        assert_eq!(parse_ttl_str(""), None);
        assert_eq!(parse_ttl_str("abc"), None);
        assert_eq!(parse_ttl_str("5x"), None);
    }

    #[test_log::test]
    fn test_ttl_from_value() {
        assert_eq!(ttl_from_value(Some(&json!(45))), Some(45));
        assert_eq!(ttl_from_value(Some(&json!("2m"))), Some(120));
        assert_eq!(ttl_from_value(Some(&json!(-1.5))), None);
        assert_eq!(ttl_from_value(Some(&json!(true))), None);
        assert_eq!(ttl_from_value(None), None);
    }
}
