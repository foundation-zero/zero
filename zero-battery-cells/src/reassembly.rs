use log::{debug, warn};
use std::collections::HashMap;

/// How far behind a fragment's last accepted counter a repeat counts as late.
///
/// Late and duplicate fragments are ignored so they cannot break up the
/// transmission in progress. Anything further behind is taken as the PLC's
/// counter having reset (e.g. a restart) and is accepted, so recovery is never
/// blocked; a reset landing within this window costs at most this many
/// transmissions.
const LATE_TRANSMISSIONS: u32 = 4;

/// Stitches the datagrams of one NetVar list transmission back into its payload.
///
/// A list larger than one datagram is transmitted as a burst of datagrams with
/// an incrementing `packet_index`. Their counters do not tie them together:
/// every packet index counts its own transmissions, so the fragments of one
/// burst carry unrelated values. A burst is therefore delimited by the packet
/// indices themselves: packet 0 opens a transmission, and a fragment whose
/// index is already buffered belongs to the next one (its packet 0 was lost).
/// Fragments are buffered per list until the declared
/// payload size is reached, then returned concatenated in `packet_index` order.
///
/// Buffers are kept per list and reused across transmissions, so once every
/// list has completed one, reassembly no longer allocates.
#[derive(Debug, Default)]
pub struct ListReassembler {
    lists: HashMap<u16, PartialList>,
}

#[derive(Debug, Default)]
struct PartialList {
    /// Last accepted counter of every packet index seen, as `(packet index, counter)`.
    counters: Vec<(u16, u32)>,
    /// Fragments of the current transmission as `(packet index, bytes)`, in arrival order.
    fragments: Vec<(u16, Vec<u8>)>,
    /// Emptied fragment buffers, handed out again to the next transmission's fragments.
    spare: Vec<Vec<u8>>,
    bytes: usize,
    /// The last completed payload; overwritten when the next one completes.
    assembled: Vec<u8>,
}

impl ListReassembler {
    /// Buffer one fragment; returns the assembled payload once it is complete.
    ///
    /// Packet 0, or a fragment whose packet index is already buffered, starts
    /// the next transmission and discards the incomplete set, which is how a
    /// lost datagram is recovered. Packet 0 resynchronises every transmission,
    /// so a lost first packet cannot leave stale fragments to pair with the
    /// next burst; fragments are only merged across transmissions when two
    /// consecutive bursts lose complementary datagrams including the second
    /// one's packet 0, and never beyond that pair. A repeat of a fragment up to
    /// [`LATE_TRANSMISSIONS`] behind its packet index's last counter is ignored
    /// instead; counter distances wrap, so the counter rolling over is just the
    /// next transmission.
    ///
    /// The returned payload borrows the reassembler and is valid until the next push.
    pub fn push(
        &mut self,
        list_id: u16,
        packet_index: u16,
        counter: u32,
        payload: &[u8],
        expected_bytes: usize,
    ) -> Option<&[u8]> {
        let partial = self.lists.entry(list_id).or_default();
        if !partial.accept_counter(packet_index, counter) {
            debug!(
                "list {}: packet {} with counter {} is a late or duplicate repeat; ignoring",
                list_id, packet_index, counter
            );
            return None;
        }

        let starts_transmission = packet_index == 0 || partial.holds(packet_index);
        if starts_transmission && partial.bytes > 0 {
            warn!(
                "list {}: transmission incomplete ({} of {} byte(s)); dropping",
                list_id, partial.bytes, expected_bytes
            );
            partial.discard_fragments();
        }

        partial.store(packet_index, payload);
        if partial.bytes < expected_bytes {
            return None;
        }
        Some(partial.assemble())
    }
}

impl PartialList {
    /// Record `counter` for `packet_index`, unless it repeats a recent one.
    fn accept_counter(&mut self, packet_index: u16, counter: u32) -> bool {
        let known = self
            .counters
            .iter_mut()
            .find(|(index, _)| *index == packet_index);
        match known {
            Some((_, last)) if last.wrapping_sub(counter) <= LATE_TRANSMISSIONS => false,
            Some((_, last)) => {
                *last = counter;
                true
            }
            None => {
                self.counters.push((packet_index, counter));
                true
            }
        }
    }

    /// Whether the current transmission already holds fragment `packet_index`.
    fn holds(&self, packet_index: u16) -> bool {
        self.fragments
            .iter()
            .any(|(index, _)| *index == packet_index)
    }

    /// Keep `payload` as fragment `packet_index` of the current transmission.
    fn store(&mut self, packet_index: u16, payload: &[u8]) {
        let mut fragment = self.spare.pop().unwrap_or_default();
        fragment.extend_from_slice(payload);
        self.fragments.push((packet_index, fragment));
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
            reassembler.push(411, 1, 55, &[3, 4, 5], 6),
            Some(&[0, 1, 2, 3, 4, 5][..])
        );
    }

    #[test]
    fn out_of_order_fragments_still_assemble_in_order() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 9, &[0, 1], 5), None);
        assert_eq!(reassembler.push(411, 2, 3, &[4], 5), None);
        assert_eq!(
            reassembler.push(411, 1, 7, &[2, 3], 5),
            Some(&[0, 1, 2, 3, 4][..])
        );
    }

    #[test]
    fn live_counters_differ_per_fragment() {
        // Two bursts of list 462 as captured live: every packet index counts
        // on its own, at a fixed offset from the others.
        let first = [5666, 5657, 5652, 5651, 5650, 5649, 5647, 5646, 5645];
        let mut reassembler = ListReassembler::default();
        for burst in 0..2 {
            for (index, counter) in first.iter().enumerate() {
                let assembled =
                    reassembler.push(462, index as u16, counter + burst, &[index as u8], 9);
                if index < first.len() - 1 {
                    assert_eq!(assembled, None);
                } else {
                    assert_eq!(assembled, Some(&[0, 1, 2, 3, 4, 5, 6, 7, 8][..]));
                }
            }
        }
    }

    #[test]
    fn packet_zero_drops_an_incomplete_transmission() {
        let mut reassembler = ListReassembler::default();
        // Packet 1 of the first transmission is lost...
        assert_eq!(reassembler.push(411, 0, 63, &[0, 1], 4), None);
        // ...so the next packet 0 starts a clean set and the old bytes are gone.
        assert_eq!(reassembler.push(411, 0, 64, &[2, 3], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 50, &[4, 5], 4),
            Some(&[2, 3, 4, 5][..])
        );
    }

    #[test]
    fn a_lost_first_packet_does_not_pair_later_transmissions() {
        let mut reassembler = ListReassembler::default();
        // Packet 0 of the first transmission is lost: packets 1 and 2 wait...
        assert_eq!(reassembler.push(411, 1, 10, &[9], 3), None);
        assert_eq!(reassembler.push(411, 2, 20, &[9], 3), None);
        // ...and are dropped by the next packet 0 instead of completing with it.
        for transmission in 1..4 {
            assert_eq!(reassembler.push(411, 0, transmission, &[0], 3), None);
            assert_eq!(reassembler.push(411, 1, 10 + transmission, &[1], 3), None);
            assert_eq!(
                reassembler.push(411, 2, 20 + transmission, &[2], 3),
                Some(&[0, 1, 2][..])
            );
        }
    }

    #[test]
    fn a_repeated_packet_index_drops_an_incomplete_transmission() {
        let mut reassembler = ListReassembler::default();
        // The first transmission loses packet 2 and the second its packet 0...
        assert_eq!(reassembler.push(411, 0, 1, &[9], 3), None);
        assert_eq!(reassembler.push(411, 1, 11, &[9], 3), None);
        // ...so the second packet 1 is what starts a clean set.
        assert_eq!(reassembler.push(411, 1, 12, &[1], 3), None);
        assert_eq!(reassembler.push(411, 2, 22, &[2], 3), None);
        assert_eq!(reassembler.push(411, 0, 3, &[0], 3), None);
        assert_eq!(reassembler.push(411, 1, 13, &[1], 3), None);
        assert_eq!(reassembler.push(411, 2, 23, &[2], 3), Some(&[0, 1, 2][..]));
    }

    #[test]
    fn a_duplicate_fragment_is_ignored() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 1, &[0, 1], 4), None);
        assert_eq!(reassembler.push(411, 0, 1, &[9, 9], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 7, &[2, 3], 4),
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
    fn reused_buffers_carry_no_stale_bytes_into_the_next_transmission() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 1, &[1, 1, 1], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 1, &[1], 4),
            Some(&[1, 1, 1, 1][..])
        );
        // Same list, shorter first fragment: the recycled buffers must be empty.
        assert_eq!(reassembler.push(411, 0, 2, &[2], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 2, &[3, 3, 3], 4),
            Some(&[2, 3, 3, 3][..])
        );
    }

    #[test]
    fn a_late_fragment_leaves_the_current_transmission_intact() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 63, &[7, 7], 4), None);
        assert!(reassembler.push(411, 1, 51, &[7, 7], 4).is_some());
        assert_eq!(reassembler.push(411, 0, 64, &[0, 1], 4), None);
        // A straggler behind packet 1's last counter must not restart the set.
        assert_eq!(reassembler.push(411, 1, 50, &[9, 9], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 52, &[2, 3], 4),
            Some(&[0, 1, 2, 3][..])
        );
    }

    #[test]
    fn a_counter_reset_is_accepted() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, 5000, &[9, 9], 4), None);
        assert!(reassembler.push(411, 1, 4990, &[9, 9], 4).is_some());
        // Far behind the last counters: the PLC restarted its counters.
        assert_eq!(reassembler.push(411, 0, 0, &[0, 1], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 0, &[2, 3], 4),
            Some(&[0, 1, 2, 3][..])
        );
    }

    #[test]
    fn the_counter_wraps_around() {
        let mut reassembler = ListReassembler::default();
        assert_eq!(reassembler.push(411, 0, u32::MAX, &[9, 9], 4), None);
        assert!(reassembler.push(411, 1, u32::MAX, &[9, 9], 4).is_some());
        assert_eq!(reassembler.push(411, 0, 0, &[0, 1], 4), None);
        // u32::MAX - 1 is now two transmissions behind, so late rather than a reset.
        assert_eq!(reassembler.push(411, 1, u32::MAX - 1, &[9, 9], 4), None);
        assert_eq!(
            reassembler.push(411, 1, 0, &[2, 3], 4),
            Some(&[0, 1, 2, 3][..])
        );
    }
}
