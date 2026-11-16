use crate::cells::{decode_pack, ModuleFrame};
use crate::config::PipelineConfig;
use crate::mapping;
use crate::netvar;
use crate::nvl::{self, PackSpec};
use crate::reassembly::ListReassembler;
use anyhow::{bail, Context, Result};
use log::{info, warn};
use std::collections::{HashMap, HashSet};
use std::net::SocketAddr;

/// Turns NetVar datagrams of the owned lists into module frames.
///
/// Holds the per-list reassembly buffers, so one decoder serves one datagram
/// stream; frames borrow nothing from it beyond the static pack names.
pub struct Decoder {
    packs: HashMap<u16, PackSpec>,
    reassembler: ListReassembler,
    preamble_reported: HashSet<u16>,
}

impl Decoder {
    /// Load the template declaration, validate it, and derive the owned packs from it.
    ///
    /// Every known pack shares the template's layout. Only lists this process owns
    /// (OWN_LIST_IDS; all known lists when unset) get decoders.
    pub fn load(config: &PipelineConfig) -> Result<Self> {
        let path = &config.nvl_file;
        let template = nvl::load_declaration(path)?;
        template.validate(path)?;

        if let Some(owned) = &config.owned_list_ids {
            mapping::validate_owned_coverage(owned)?;
        }

        let mut packs = HashMap::new();
        for (list_id, pack) in mapping::KNOWN_PACKS {
            if let Some(owned) = &config.owned_list_ids {
                if !owned.contains(&list_id) {
                    info!(
                        "list {} (pack {}): decoded by another replica, skipping",
                        list_id, pack
                    );
                    continue;
                }
            }
            let spec = template.for_list_id(list_id)?;
            info!(
                "list {} (pack {}): {} cell voltages, {} temperatures, {} declared byte(s)",
                list_id, spec.pack, spec.voltage_count, spec.temperature_count, spec.declared_bytes
            );
            packs.insert(spec.list_id, spec);
        }

        if packs.is_empty() {
            bail!("no packs are owned by this process; check OWN_LIST_IDS");
        }
        Ok(Self {
            packs,
            reassembler: ListReassembler::default(),
            preamble_reported: HashSet::new(),
        })
    }

    /// Parse one datagram and, once it completes its pack, the pack's module frames.
    ///
    /// A datagram is one fragment of a pack's payload: it is buffered until the
    /// whole pack is present. `Ok(None)` means the pack is still incomplete; an
    /// error is the reason to drop the datagram. The frames are decoded lazily
    /// from the reassembly buffer, so this must be drained before the next call.
    pub fn decode(
        &mut self,
        source: SocketAddr,
        bytes: &[u8],
    ) -> Result<Option<impl Iterator<Item = ModuleFrame<'static>> + '_>> {
        let parsed =
            netvar::parse_datagram(bytes).context("NetVar header does not match the protocol")?;
        let header = parsed.header;

        let spec = self.packs.get(&header.list_id).with_context(|| {
            format!(
                "list {} is not decoded by this process (undeclared, or owned by another replica)",
                header.list_id
            )
        })?;

        note_preamble(&mut self.preamble_reported, header.list_id, parsed.preamble);

        let Some(assembled) = self.reassembler.push(
            header.list_id,
            header.packet_index,
            header.counter,
            parsed.payload,
            spec.declared_bytes as usize,
        ) else {
            return Ok(None);
        };

        let frames = decode_pack(
            spec.pack,
            assembled,
            spec.voltage_count,
            spec.temperature_count,
        )
        .with_context(|| format!("payload of list {} from {}", header.list_id, source))?;
        Ok(Some(frames))
    }
}

/// Warn once per list when the preamble differs from the reference format.
fn note_preamble(reported: &mut HashSet<u16>, list_id: u16, preamble: &[u8]) {
    if !netvar::has_known_preamble(preamble) && reported.insert(list_id) {
        warn!(
            "list {}: unexpected NetVar preamble {:02x?}; confirm against a live capture",
            list_id, preamble
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cells::{MILLIVOLTS_PER_VOLT, MODULES_PER_STRING, PAYLOAD_BYTES, STRINGS_PER_PACK};
    use crate::config::AppConfig;
    use crate::netvar::{HEADER_LEN, KNOWN_PREAMBLE_PREFIX};

    const DECLARATION: &str = "spec/KEB6_FOX_05_41_1_NVL_Declaration.txt";
    /// Payload bytes per datagram, as in the bench capture.
    const FRAGMENT_BYTES: usize = 256;

    fn source() -> SocketAddr {
        "192.168.102.26:60278".parse().unwrap()
    }

    fn pipeline(owned_list_ids: Option<Vec<u16>>) -> PipelineConfig {
        PipelineConfig {
            app: AppConfig {
                mqtt_host: "localhost".to_string(),
                mqtt_port: 1883,
                mqtt_prefix: "battery".to_string(),
                udp_port: 50001,
                mqtt_username: None,
                mqtt_password: None,
            },
            nvl_file: DECLARATION.to_string(),
            owned_list_ids,
        }
    }

    /// One NetVar datagram carrying `payload` as fragment `packet_index` of `list_id`.
    fn datagram(list_id: u16, packet_index: u16, counter: u32, payload: &[u8]) -> Vec<u8> {
        let mut datagram = Vec::with_capacity(HEADER_LEN + payload.len());
        datagram.extend_from_slice(KNOWN_PREAMBLE_PREFIX);
        datagram.extend_from_slice(&[0u8; 4]);
        datagram.extend_from_slice(&list_id.to_le_bytes());
        datagram.extend_from_slice(&packet_index.to_le_bytes());
        datagram.extend_from_slice(&((payload.len() / 2) as u16).to_le_bytes());
        datagram.extend_from_slice(&((HEADER_LEN + payload.len()) as u16).to_le_bytes());
        datagram.extend_from_slice(&counter.to_le_bytes());
        datagram.extend_from_slice(payload);
        datagram
    }

    /// A full pack payload where each value is its flat index, split into datagrams.
    fn pack_datagrams(list_id: u16) -> Vec<Vec<u8>> {
        let payload: Vec<u8> = (0..PAYLOAD_BYTES / 2)
            .flat_map(|index| (index as i16).to_le_bytes())
            .collect();
        payload
            .chunks(FRAGMENT_BYTES)
            .enumerate()
            .map(|(packet_index, fragment)| datagram(list_id, packet_index as u16, 1, fragment))
            .collect()
    }

    fn owned_lists(decoder: &Decoder) -> Vec<u16> {
        let mut list_ids: Vec<u16> = decoder.packs.keys().copied().collect();
        list_ids.sort_unstable();
        list_ids
    }

    #[test]
    fn load_decodes_every_known_list_by_default() {
        let decoder = Decoder::load(&pipeline(None)).unwrap();
        let known: Vec<u16> = mapping::KNOWN_PACKS.iter().map(|(id, _)| *id).collect();
        assert_eq!(owned_lists(&decoder), known);
        assert_eq!(decoder.packs[&462].pack, "46-2");
    }

    #[test]
    fn load_skips_lists_owned_by_another_replica() {
        let decoder = Decoder::load(&pipeline(Some(vec![413, 411]))).unwrap();
        assert_eq!(owned_lists(&decoder), vec![411, 413]);
    }

    #[test]
    fn load_rejects_unknown_owned_lists() {
        let error = Decoder::load(&pipeline(Some(vec![411, 999])))
            .err()
            .expect("an unknown list should be rejected");
        assert!(error.to_string().contains("not a known list id"), "{error}");
    }

    #[test]
    fn load_fails_on_a_missing_declaration() {
        let mut config = pipeline(None);
        config.nvl_file = "spec/missing.txt".to_string();
        let error = Decoder::load(&config)
            .err()
            .expect("a missing file should be rejected");
        assert!(error.to_string().contains("spec/missing.txt"), "{error}");
    }

    #[test]
    fn decode_yields_module_frames_once_the_pack_is_complete() {
        let mut decoder = Decoder::load(&pipeline(Some(vec![412]))).unwrap();
        let datagrams = pack_datagrams(412);
        let (last, fragments) = datagrams.split_last().unwrap();
        for fragment in fragments {
            assert!(decoder.decode(source(), fragment).unwrap().is_none());
        }

        let frames: Vec<_> = decoder
            .decode(source(), last)
            .unwrap()
            .expect("the last fragment completes the pack")
            .collect();
        assert_eq!(frames.len(), STRINGS_PER_PACK * MODULES_PER_STRING);
        assert!(frames.iter().all(|frame| frame.pack == "41-2"));
        let second = &frames[1];
        assert_eq!((second.string, second.module), (1, 2));
        assert_eq!(second.voltages_v[0], 14.0 / MILLIVOLTS_PER_VOLT);
    }

    #[test]
    fn decode_rejects_lists_this_process_does_not_own() {
        let mut decoder = Decoder::load(&pipeline(Some(vec![411]))).unwrap();
        let error = decoder
            .decode(source(), &datagram(412, 0, 1, &[0; 4]))
            .err()
            .expect("a list owned elsewhere should be rejected");
        assert!(
            error.to_string().contains("not decoded by this process"),
            "{error}"
        );
    }

    #[test]
    fn decode_rejects_datagrams_with_a_broken_header() {
        let mut decoder = Decoder::load(&pipeline(None)).unwrap();
        let mut truncated = datagram(411, 0, 1, &[0; 4]);
        truncated.pop();
        let error = decoder
            .decode(source(), &truncated)
            .err()
            .expect("a length mismatch should be rejected");
        assert!(error.to_string().contains("NetVar header"), "{error}");
    }

    #[test]
    fn decode_rejects_a_pack_larger_than_declared() {
        let mut decoder = Decoder::load(&pipeline(Some(vec![411]))).unwrap();
        let oversized = vec![0u8; PAYLOAD_BYTES + 2];
        let error = decoder
            .decode(source(), &datagram(411, 0, 1, &oversized))
            .err()
            .expect("an oversized payload should be rejected");
        assert!(error.to_string().contains("payload of list 411"), "{error}");
    }

    #[test]
    fn an_unexpected_preamble_is_reported_once_per_list() {
        let mut reported = HashSet::new();
        note_preamble(&mut reported, 411, b"\0-S3\0\0\0\0");
        assert!(reported.is_empty());

        note_preamble(&mut reported, 411, b"\0-S4\0\0\0\0");
        note_preamble(&mut reported, 411, b"\0-S4\0\0\0\0");
        assert_eq!(reported, HashSet::from([411]));
    }
}
