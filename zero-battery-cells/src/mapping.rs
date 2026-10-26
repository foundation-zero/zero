use anyhow::{bail, Context, Result};

/// Every list the PLCs send, with its pack name as used in MQTT topics:
/// KEB6 (41-x, 42-x), KEB7 (43-x, 44-x), KEB8 (45-x), KEB9 (46-x).
///
/// All packs share one layout, so the decoders are derived from a single
/// template declaration for exactly these lists. The names are static so
/// decoded frames can borrow them for the lifetime of the process.
pub const KNOWN_PACKS: [(u16, &str); 22] = [
    (411, "41-1"),
    (412, "41-2"),
    (413, "41-3"),
    (414, "41-4"),
    (421, "42-1"),
    (422, "42-2"),
    (423, "42-3"),
    (431, "43-1"),
    (432, "43-2"),
    (433, "43-3"),
    (441, "44-1"),
    (442, "44-2"),
    (443, "44-3"),
    (444, "44-4"),
    (451, "45-1"),
    (452, "45-2"),
    (453, "45-3"),
    (454, "45-4"),
    (461, "46-1"),
    (462, "46-2"),
    (463, "46-3"),
    (464, "46-4"),
];

/// Pack name of a known NetVar list id: `411` -> `"41-1"`.
pub fn pack_name(list_id: u16) -> Option<&'static str> {
    KNOWN_PACKS
        .iter()
        .find(|(known, _)| *known == list_id)
        .map(|(_, pack)| *pack)
}

/// NetVar list id for a pack name: `"41-1"` -> `411`.
pub fn list_id(pack: &str) -> Result<u16> {
    let digits: String = pack.chars().filter(char::is_ascii_digit).collect();
    if digits.is_empty() {
        bail!("pack '{}' contains no list id digits", pack);
    }
    digits
        .parse()
        .with_context(|| format!("pack '{}' does not map to a numeric list id", pack))
}

/// Parse the optional `OWN_LIST_IDS` JSON array.
pub fn parse_owned_list_ids(raw: &str) -> Result<Vec<u16>> {
    let list_ids: Vec<u16> =
        serde_json::from_str(raw).context("OWN_LIST_IDS must be a JSON array of list ids")?;
    if list_ids.is_empty() {
        bail!("OWN_LIST_IDS must name at least one list id");
    }
    Ok(list_ids)
}

/// Check that every list this process is told to own is a known list.
pub fn validate_owned_coverage(owned: &[u16]) -> Result<()> {
    for list_id in owned {
        if pack_name(*list_id).is_none() {
            bail!("owned list {} is not a known list id", list_id);
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn pack_names_and_list_ids_round_trip() {
        assert_eq!(pack_name(411), Some("41-1"));
        assert_eq!(pack_name(464), Some("46-4"));
        assert_eq!(pack_name(415), None);
    }

    #[test]
    fn list_id_rejects_names_without_digits() {
        assert!(list_id("nope").is_err());
    }

    #[test]
    fn owned_list_ids_parse_and_reject_empty_arrays() {
        assert_eq!(parse_owned_list_ids("[411, 413]").unwrap(), vec![411, 413]);
        assert!(parse_owned_list_ids("[]").is_err());
    }

    #[test]
    fn owned_coverage_requires_known_lists() {
        assert!(validate_owned_coverage(&[411, 464]).is_ok());
        let error = validate_owned_coverage(&[411, 999]).unwrap_err();
        assert!(error.to_string().contains("not a known list id"), "{error}");
    }

    #[test]
    fn known_packs_are_unique_and_round_trip() {
        let unique: HashSet<u16> = KNOWN_PACKS.iter().map(|(list_id, _)| *list_id).collect();
        assert_eq!(unique.len(), KNOWN_PACKS.len());
        for (id, pack) in KNOWN_PACKS {
            assert_eq!(list_id(pack).unwrap(), id);
        }
    }
}
