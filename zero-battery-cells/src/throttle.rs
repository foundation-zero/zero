/// Whether the `count`-th occurrence (1-based) of a repeating problem should be
/// logged: the first one, then every `interval`-th.
///
/// Keeps an outage readable in the logs: log lines fire at bounded frequency
/// while every occurrence still counts toward the next line.
pub fn log_event(count: u64, interval: u64) -> bool {
    count == 1 || count.is_multiple_of(interval)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn logs_the_first_and_every_interval() {
        assert!(log_event(1, 500));
        assert!(!log_event(2, 500));
        assert!(!log_event(499, 500));
        assert!(log_event(500, 500));
        assert!(log_event(1000, 500));
    }
}
