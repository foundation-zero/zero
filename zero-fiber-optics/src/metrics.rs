//! Pipeline counters shared across tasks.
//!
//! The pipeline used to fail silently: a stalled MQTT publish blocked the parser,
//! which filled the packet channel, which stopped the UDP listener from reading,
//! and the kernel dropped every datagram without the process logging anything.
//! These counters exist so each stage of that chain is visible in the logs.

use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;

/// Per-port counters shared by the UDP listener, parser and watchdog tasks.
#[derive(Debug, Default)]
pub struct PortMetrics {
    received: AtomicU64,
    queue_dropped: AtomicU64,
    parse_errors: AtomicU64,
    length_mismatches: AtomicU64,
    enqueued: AtomicU64,
    publish_errors: AtomicU64,
    publish_timeouts: AtomicU64,
    first_packet_seen: AtomicBool,
}

/// Point-in-time copy of [`PortMetrics`], suitable for logging.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct PortSnapshot {
    pub received: u64,
    pub queue_dropped: u64,
    pub parse_errors: u64,
    pub length_mismatches: u64,
    pub enqueued: u64,
    pub publish_errors: u64,
    pub publish_timeouts: u64,
}

impl PortMetrics {
    /// Counters are read from several tasks, so they are shared behind an `Arc`.
    pub fn new() -> Arc<Self> {
        Arc::new(Self::default())
    }

    /// Count a datagram read from the socket. Returns the new total.
    pub fn incr_received(&self) -> u64 {
        increment(&self.received)
    }

    /// Count a datagram discarded because the parser could not keep up.
    pub fn incr_queue_dropped(&self) -> u64 {
        increment(&self.queue_dropped)
    }

    /// Count a datagram the parser could not decode.
    pub fn incr_parse_errors(&self) -> u64 {
        increment(&self.parse_errors)
    }

    /// Count a datagram whose size differs from the configured schema.
    pub fn incr_length_mismatches(&self) -> u64 {
        increment(&self.length_mismatches)
    }

    /// Count a packet handed to the MQTT event loop.
    ///
    /// This is not delivery. A packet counted here can still be rejected or
    /// ignored by the broker; see [`MqttMetrics::incr_acked`] for the broker side.
    pub fn incr_enqueued(&self) -> u64 {
        increment(&self.enqueued)
    }

    /// Count a publish the event loop rejected or could not serialize.
    pub fn incr_publish_errors(&self) -> u64 {
        increment(&self.publish_errors)
    }

    /// Count a publish abandoned because the event loop stopped draining requests.
    pub fn incr_publish_timeouts(&self) -> u64 {
        increment(&self.publish_timeouts)
    }

    /// Datagrams received so far.
    pub fn received(&self) -> u64 {
        self.received.load(Ordering::Relaxed)
    }

    /// Returns `true` exactly once, on the first datagram seen on this port.
    pub fn mark_first_packet(&self) -> bool {
        !self.first_packet_seen.swap(true, Ordering::Relaxed)
    }

    /// Copy of all counters at this instant.
    pub fn snapshot(&self) -> PortSnapshot {
        PortSnapshot {
            received: self.received(),
            queue_dropped: self.queue_dropped.load(Ordering::Relaxed),
            parse_errors: self.parse_errors.load(Ordering::Relaxed),
            length_mismatches: self.length_mismatches.load(Ordering::Relaxed),
            enqueued: self.enqueued.load(Ordering::Relaxed),
            publish_errors: self.publish_errors.load(Ordering::Relaxed),
            publish_timeouts: self.publish_timeouts.load(Ordering::Relaxed),
        }
    }
}

/// Counters for the shared MQTT connection, written by the event loop and by
/// publishers, read by the watchdog.
#[derive(Debug, Default)]
pub struct MqttMetrics {
    connects: AtomicU64,
    reconnects: AtomicU64,
    enqueued: AtomicU64,
    acked: AtomicU64,
    publish_errors: AtomicU64,
    publish_timeouts: AtomicU64,
    puback_denied: AtomicU64,
    server_disconnects: AtomicU64,
}

/// Point-in-time copy of [`MqttMetrics`], suitable for logging.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct MqttSnapshot {
    pub connects: u64,
    pub reconnects: u64,
    pub enqueued: u64,
    pub acked: u64,
    pub publish_errors: u64,
    pub publish_timeouts: u64,
    pub puback_denied: u64,
    pub server_disconnects: u64,
}

impl MqttMetrics {
    /// Counters are shared between the event loop task and every publisher.
    pub fn new() -> Arc<Self> {
        Arc::new(Self::default())
    }

    /// Count a CONNACK, successful or rejected.
    pub fn incr_connects(&self) -> u64 {
        increment(&self.connects)
    }

    /// Count a failed poll followed by a reconnect attempt.
    pub fn incr_reconnects(&self) -> u64 {
        increment(&self.reconnects)
    }

    /// Count a publish handed to the event loop.
    ///
    /// This records acceptance by the local event loop, not delivery. `enqueued`
    /// running ahead of `acked` means the broker has stopped acknowledging
    /// publishes, which is what a resource alarm or a dead connection looks like
    /// from here.
    pub fn incr_enqueued(&self) -> u64 {
        increment(&self.enqueued)
    }

    /// Count a PUBACK the broker returned with a success reason code.
    ///
    /// The only counter that reflects the broker having taken the message.
    pub fn incr_acked(&self) -> u64 {
        increment(&self.acked)
    }

    /// Count a publish the event loop rejected or could not serialize.
    pub fn incr_publish_errors(&self) -> u64 {
        increment(&self.publish_errors)
    }

    /// Count a publish abandoned after exhausting the publish timeout.
    pub fn incr_publish_timeouts(&self) -> u64 {
        increment(&self.publish_timeouts)
    }

    /// Count a PUBACK carrying a non-success reason code.
    pub fn incr_puback_denied(&self) -> u64 {
        increment(&self.puback_denied)
    }

    /// Count a DISCONNECT initiated by the broker.
    pub fn incr_server_disconnects(&self) -> u64 {
        increment(&self.server_disconnects)
    }

    /// Copy of all counters at this instant.
    pub fn snapshot(&self) -> MqttSnapshot {
        MqttSnapshot {
            connects: self.connects.load(Ordering::Relaxed),
            reconnects: self.reconnects.load(Ordering::Relaxed),
            enqueued: self.enqueued.load(Ordering::Relaxed),
            acked: self.acked.load(Ordering::Relaxed),
            publish_errors: self.publish_errors.load(Ordering::Relaxed),
            publish_timeouts: self.publish_timeouts.load(Ordering::Relaxed),
            puback_denied: self.puback_denied.load(Ordering::Relaxed),
            server_disconnects: self.server_disconnects.load(Ordering::Relaxed),
        }
    }
}

/// Whether the n-th repeat of a recurring problem should be logged.
///
/// At 10 Hz a stalled pipeline produces an event per packet, so logging every one
/// would drown the output; powers of two plus every thousandth keep the signal.
pub fn should_log_repeated(count: u64) -> bool {
    count.is_power_of_two() || count.is_multiple_of(1000)
}

fn increment(counter: &AtomicU64) -> u64 {
    counter.fetch_add(1, Ordering::Relaxed) + 1
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn port_counters_accumulate_and_snapshot() {
        let metrics = PortMetrics::new();

        metrics.incr_received();
        metrics.incr_received();
        metrics.incr_queue_dropped();
        metrics.incr_parse_errors();
        metrics.incr_length_mismatches();
        metrics.incr_enqueued();
        metrics.incr_publish_errors();
        metrics.incr_publish_timeouts();

        assert_eq!(
            metrics.snapshot(),
            PortSnapshot {
                received: 2,
                queue_dropped: 1,
                parse_errors: 1,
                length_mismatches: 1,
                enqueued: 1,
                publish_errors: 1,
                publish_timeouts: 1,
            }
        );
        assert_eq!(metrics.received(), 2);
    }

    #[test]
    fn mark_first_packet_only_fires_once() {
        let metrics = PortMetrics::new();

        assert!(metrics.mark_first_packet());
        assert!(!metrics.mark_first_packet());
        assert!(!metrics.mark_first_packet());
    }

    #[test]
    fn mqtt_counters_accumulate_and_snapshot() {
        let metrics = MqttMetrics::new();

        metrics.incr_connects();
        metrics.incr_reconnects();
        metrics.incr_enqueued();
        metrics.incr_acked();
        metrics.incr_publish_errors();
        metrics.incr_publish_timeouts();
        metrics.incr_puback_denied();
        metrics.incr_server_disconnects();

        assert_eq!(
            metrics.snapshot(),
            MqttSnapshot {
                connects: 1,
                reconnects: 1,
                enqueued: 1,
                acked: 1,
                publish_errors: 1,
                publish_timeouts: 1,
                puback_denied: 1,
                server_disconnects: 1,
            }
        );
    }

    #[test]
    fn repeated_logging_is_rate_limited() {
        assert!(should_log_repeated(1));
        assert!(!should_log_repeated(3));
        assert!(should_log_repeated(4));
        assert!(should_log_repeated(1000));
        assert!(!should_log_repeated(1001));
    }
}
