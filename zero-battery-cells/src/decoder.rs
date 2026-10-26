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
