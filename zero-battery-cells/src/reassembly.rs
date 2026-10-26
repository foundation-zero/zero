use log::{debug, warn};
use std::collections::HashMap;

/// How many cycles behind the current one a fragment counts as merely late.
///
/// Late fragments are ignored so they cannot break up the cycle in progress.
/// Anything further behind is taken as the PLC's counter having reset (e.g. a
/// restart) and starts a fresh cycle, so recovery is never blocked; a reset
/// landing within this window costs at most this many cycles.
const LATE_CYCLES: u32 = 4;

/// Stitches per-cycle datagrams of one NetVar list back into its full payload.
///
/// A list larger than one datagram is transmitted as several datagrams that
/// share a `cycle` and carry an incrementing `packet_index`. Fragments are
/// buffered per list until the declared payload size is reached, then returned
/// concatenated in `packet_index` order.
///
/// Buffers are kept per list and reused across cycles, so once every list has
/// completed a cycle, reassembly no longer allocates.
#[derive(Debug, Default)]
pub struct ListReassembler {
    lists: HashMap<u16, PartialList>,
}

#[derive(Debug, Default)]
struct PartialList {
    cycle: Option<u32>,
    /// Fragments of the current cycle as `(packet index, bytes)`, in arrival order.
    fragments: Vec<(u16, Vec<u8>)>,
    /// Emptied fragment buffers, handed out again to the next cycle's fragments.
    spare: Vec<Vec<u8>>,
    bytes: usize,
    /// The last completed payload; overwritten when the next one completes.
    assembled: Vec<u8>,
}

impl ListReassembler {
    /// Buffer one fragment; returns the assembled payload once it is complete.
    ///
    /// A new cycle discards any still-incomplete fragment set, which is how a
    /// lost datagram is recovered: the next cycle starts clean instead of
    /// merging fragments across cycles. Fragments of a recent earlier cycle
    /// (see [`LATE_CYCLES`]) are ignored instead; cycle distances wrap, so the
    /// counter rolling over is just the next cycle.
    ///
    /// The returned payload borrows the reassembler and is valid until the next push.
    pub fn push(
        &mut self,
        list_id: u16,
        packet_index: u16,
        cycle: u32,
        payload: &[u8],
        expected_bytes: usize,
    ) -> Option<&[u8]> {
        let partial = self.lists.entry(list_id).or_default();
        if partial.cycle != Some(cycle) {
            if let Some(current) = partial.cycle {
                if current.wrapping_sub(cycle) <= LATE_CYCLES {
                    debug!(
                        "list {}: fragment of cycle {} arrived during cycle {}; ignoring",
                        list_id, cycle, current
                    );
                    return None;
                }
            }
            if partial.bytes > 0 {
                warn!(
                    "list {}: cycle {:?} incomplete ({} of {} byte(s)); dropping",
                    list_id, partial.cycle, partial.bytes, expected_bytes
                );
            }
            partial.discard_fragments();
            partial.cycle = Some(cycle);
        }

        partial.store(packet_index, payload);
        if partial.bytes < expected_bytes {
            return None;
        }
        Some(partial.assemble())
    }
}

impl PartialList {
    /// Keep `payload` as fragment `packet_index`, replacing a duplicate.
    fn store(&mut self, packet_index: u16, payload: &[u8]) {
        let existing = self
            .fragments
            .iter_mut()
            .find(|(index, _)| *index == packet_index);
        match existing {
            Some((_, fragment)) => {
                self.bytes -= fragment.len();
                fragment.clear();
                fragment.extend_from_slice(payload);
            }
            None => {
                let mut fragment = self.spare.pop().unwrap_or_default();
                fragment.extend_from_slice(payload);
                self.fragments.push((packet_index, fragment));
            }
        }
        self.bytes += payload.len();
    }

    /// Concatenate the fragments in packet-index order and start a clean set.
    fn assemble(&mut self) -> &[u8] {
        self.fragments.sort_unstable_by_key(|(index, _)| *index);
        self.assembled.clear();
        for (_, fragment) in &self.fragments {
            self.assembled.extend_from_slice(fragment);
        }
        self.discard_fragments();
        &self.assembled
    }

    /// Empty the fragment set, keeping its buffers for reuse.
    fn discard_fragments(&mut self) {
        self.spare
            .extend(self.fragments.drain(..).map(|(_, mut fragment)| {
                fragment.clear();
                fragment
            }));
        self.bytes = 0;
    }
}
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fragments_assemble_in_packet_index_order() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 63, &[0, 1, 2], 6), None);
        assert_eq!(
            reassembler.push(411, 1, 63, &[3, 4, 5], 6),
            Some(&[0, 1, 2, 3, 4, 5][..])
        );
    }

    #[test]
    fn out_of_order_fragments_still_assemble_in_order() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 1, 7, &[3, 4], 5), None);
        assert_eq!(
            reassembler.push(411, 0, 7, &[0, 1, 2], 5),
            Some(&[0, 1, 2, 3, 4][..])
        );
    }

    #[test]
    fn a_new_cycle_drops_an_incomplete_fragment_set() {
        let mut reassembler = ListReassembler::default();
        // Cycle 63 is left half-finished...
        assert_eq!(reassembler.push(411, 0, 63, &[0, 1], 4), None);
        // ...and a cycle 64 fragment starts a clean set, so 63's bytes are gone.
        assert_eq!(reassembler.push(411, 0, 64, &[2, 3], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 64, &[4, 5], 4),
            Some(&[2, 3, 4, 5][..])
        );
    }

    #[test]
    fn duplicate_packet_index_overwrites() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 1, &[9, 9], 4), None);
        assert_eq!(reassembler.push(411, 0, 1, &[0, 1], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 1, &[2, 3], 4),
            Some(&[0, 1, 2, 3][..])
        );
    }

    #[test]
    fn lists_are_reassembled_independently() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 1, &[0], 2), None);
        assert_eq!(reassembler.push(412, 0, 1, &[9], 2), None);
        assert_eq!(reassembler.push(411, 1, 1, &[1], 2), Some(&[0, 1][..]));
        assert_eq!(reassembler.push(412, 1, 1, &[8], 2), Some(&[9, 8][..]));
    }

    #[test]
    fn reused_buffers_carry_no_stale_bytes_into_the_next_cycle() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 1, &[1, 1, 1], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 1, &[1], 4),
            Some(&[1, 1, 1, 1][..])
        );
        // Same list, shorter first fragment: the recycled buffers must be empty.
        assert_eq!(reassembler.push(411, 1, 2, &[3, 3], 4), None);
        assert_eq!(
            reassembler.push(411, 0, 2, &[2, 2], 4),
            Some(&[2, 2, 3, 3][..])
        );
    }

    #[test]
    fn a_late_fragment_leaves_the_current_cycle_intact() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 64, &[0, 1], 4), None);
        // A straggler from cycle 63 must not discard cycle 64's first fragment.
        assert_eq!(reassembler.push(411, 1, 63, &[9, 9], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 64, &[2, 3], 4),
            Some(&[0, 1, 2, 3][..])
        );
    }

    #[test]
    fn a_counter_reset_starts_a_fresh_cycle() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 5000, &[9, 9], 4), None);
        // Far behind the current cycle: the PLC restarted its counter.
        assert_eq!(reassembler.push(411, 0, 0, &[0, 1], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 0, &[2, 3], 4),
            Some(&[0, 1, 2, 3][..])
        );
    }

    #[test]
    fn the_cycle_counter_wraps_around() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, u32::MAX, &[9, 9], 4), None);
        assert_eq!(reassembler.push(411, 0, 0, &[0, 1], 4), None);
        // u32::MAX is now one cycle behind, so late rather than a reset.
        assert_eq!(reassembler.push(411, 1, u32::MAX, &[9, 9], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 0, &[2, 3], 4),
            Some(&[0, 1, 2, 3][..])
        );
    }
}
