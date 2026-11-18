//! Pod readiness for the chart's exec probe (ADR 0001).

use log::{debug, error};
use std::path::PathBuf;
use std::sync::{Arc, Mutex, MutexGuard};
use std::time::{SystemTime, UNIX_EPOCH};

/// Status file the chart's exec readiness probe prints; ready when it starts with `ready:`.
pub const STATUS_FILE: &str = "/tmp/ready";

/// Kubernetes shows this file's contents as the container's termination message.
const TERMINATION_LOG: &str = "/dev/termination-log";

/// Whether the pod can do its job, mirrored to a status file for the readiness probe.
///
/// Clones share one state. Each change rewrites the file with one line, such as
/// `not ready: mqtt: connection refused since 13:02:05 UTC`.
#[derive(Debug, Clone)]
pub struct Readiness {
    path: PathBuf,
    status: Arc<Mutex<Status>>,
}

#[derive(Debug)]
struct Status {
    ready: bool,
    reason: String,
    /// When `ready` last changed, as a UTC time of day for the status line.
    since: String,
}

impl Status {
    fn line(&self) -> String {
        let state = if self.ready { "ready" } else { "not ready" };
        format!("{state}: {} since {} UTC", self.reason, self.since)
    }
}

impl Readiness {
    /// Start not ready for `reason`, and write the status file.
    pub fn new(path: impl Into<PathBuf>, reason: impl Into<String>) -> Self {
        let readiness = Self {
            path: path.into(),
            status: Arc::new(Mutex::new(Status {
                ready: false,
                reason: reason.into(),
                since: utc_clock(SystemTime::now()),
            })),
        };
        readiness.write(&readiness.lock());
        readiness
    }

    /// Mark the pod ready.
    pub fn ready(&self, reason: impl Into<String>) {
        self.set(true, reason.into());
    }

    /// Mark the pod not ready. A new reason while already not ready keeps the
    /// original `since`, so the status line shows when the outage started.
    pub fn not_ready(&self, reason: impl Into<String>) {
        self.set(false, reason.into());
    }

    fn set(&self, ready: bool, reason: String) {
        let mut status = self.lock();
        if status.ready == ready && status.reason == reason {
            return;
        }
        if status.ready != ready {
            status.since = utc_clock(SystemTime::now());
        }
        status.ready = ready;
        status.reason = reason;
        self.write(&status);
    }

    fn lock(&self) -> MutexGuard<'_, Status> {
        // A panic while holding the lock leaves the status valid, so a poisoned lock is usable.
        self.status
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
    }

    /// Write via a rename, so the probe never reads a half-written file.
    fn write(&self, status: &Status) {
        let staging = self.path.with_extension("tmp");
        let written = std::fs::write(&staging, status.line() + "\n")
            .and_then(|()| std::fs::rename(&staging, &self.path));
        if let Err(e) = written {
            error!(
                "Failed to write readiness to {}: {}",
                self.path.display(),
                e
            );
        }
    }
}

/// Record why the container is about to exit, for `kubectl describe` and the pod events.
pub fn write_termination_message(message: &str) {
    if let Err(e) = std::fs::write(TERMINATION_LOG, message) {
        // Outside Kubernetes the file does not exist; the log line says the same.
        debug!("Failed to write {}: {}", TERMINATION_LOG, e);
    }
}

fn utc_clock(time: SystemTime) -> String {
    let seconds = time
        .duration_since(UNIX_EPOCH)
        .map(|since| since.as_secs())
        .unwrap_or_default()
        % 86_400;
    format!(
        "{:02}:{:02}:{:02}",
        seconds / 3600,
        seconds / 60 % 60,
        seconds % 60
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    fn status_file(name: &str) -> PathBuf {
        let directory = std::env::temp_dir().join(format!("readiness-{}", std::process::id()));
        std::fs::create_dir_all(&directory).unwrap();
        directory.join(name)
    }

    fn read(path: &std::path::Path) -> String {
        std::fs::read_to_string(path).unwrap()
    }

    #[test]
    fn status_file_follows_the_state() {
        let path = status_file("follows");
        let readiness = Readiness::new(&path, "mqtt: connecting");
        assert!(read(&path).starts_with("not ready: mqtt: connecting since "));

        readiness.ready("mqtt connected");
        assert!(read(&path).starts_with("ready: mqtt connected since "));

        readiness.not_ready("mqtt: connection refused");
        let line = read(&path);
        assert!(line.starts_with("not ready: mqtt: connection refused since "));
        assert!(line.ends_with(" UTC\n"));
    }

    #[test]
    fn a_new_reason_keeps_when_the_outage_started() {
        let path = status_file("since");
        let readiness = Readiness::new(&path, "mqtt: connecting");
        let since = |line: String| line.rsplit_once(" since ").unwrap().1.to_owned();
        let first = since(read(&path));

        // Past the next whole second, so a reset `since` would show.
        std::thread::sleep(Duration::from_millis(1100));
        readiness.not_ready("mqtt: connection refused");

        assert!(read(&path).starts_with("not ready: mqtt: connection refused since "));
        assert_eq!(since(read(&path)), first);
    }

    #[test]
    fn an_unchanged_status_is_not_rewritten() {
        let path = status_file("unchanged");
        let readiness = Readiness::new(&path, "mqtt: connecting");
        std::fs::remove_file(&path).unwrap();

        readiness.not_ready("mqtt: connecting");

        assert!(!path.exists());
    }

    #[test]
    fn a_status_file_that_cannot_be_written_does_not_panic() {
        let path = status_file("missing-directory").join("ready");
        let readiness = Readiness::new(&path, "mqtt: connecting");
        readiness.ready("mqtt connected");

        assert!(!path.exists());
    }

    #[test]
    fn utc_clock_formats_the_time_of_day() {
        let time = UNIX_EPOCH + Duration::from_secs(3 * 86_400 + 13 * 3600 + 2 * 60 + 5);
        assert_eq!(utc_clock(time), "13:02:05");
    }
}
