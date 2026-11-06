use log::{debug, error};
use std::path::PathBuf;
use std::sync::{Arc, Mutex, MutexGuard};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::time::Instant;

/// Status file the chart's exec readiness probe prints; ready when it starts with `ready:`.
pub const STATUS_FILE: &str = "/tmp/ready";

/// Exit after this long not ready (ADR 0001). Longer than the kubelet's 10 minute
/// backoff reset, so these exits never add up to `CrashLoopBackOff`.
pub const NOT_READY_DEADLINE: Duration = Duration::from_secs(15 * 60);

/// Kubernetes shows this file's contents as the container's termination message.
const TERMINATION_LOG: &str = "/dev/termination-log";

/// Upper bound on how long [`Readiness::deadline`] sleeps between checks.
const DEADLINE_CHECK_INTERVAL: Duration = Duration::from_secs(10);

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
    /// When `ready` last changed; the deadline counts from here.
    since: Instant,
    /// Wall-clock form of `since`, for the status line.
    since_clock: String,
}

impl Status {
    fn line(&self) -> String {
        let state = if self.ready { "ready" } else { "not ready" };
        format!("{state}: {} since {} UTC", self.reason, self.since_clock)
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
                since: Instant::now(),
                since_clock: utc_clock(SystemTime::now()),
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
    /// original `since`, so the deadline is not reset by a different error.
    pub fn not_ready(&self, reason: impl Into<String>) {
        self.set(false, reason.into());
    }

    /// Resolve with the status line once the pod has been not ready for `limit`.
    pub async fn deadline(&self, limit: Duration) -> String {
        loop {
            let wait = {
                let status = self.lock();
                if status.ready {
                    DEADLINE_CHECK_INTERVAL
                } else {
                    match limit.checked_sub(status.since.elapsed()) {
                        Some(left) if !left.is_zero() => left.min(DEADLINE_CHECK_INTERVAL),
                        _ => return status.line(),
                    }
                }
            };
            tokio::time::sleep(wait).await;
        }
    }

    fn set(&self, ready: bool, reason: String) {
        let mut status = self.lock();
        if status.ready == ready && status.reason == reason {
            return;
        }
        if status.ready != ready {
            status.since = Instant::now();
            status.since_clock = utc_clock(SystemTime::now());
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

    fn status_file(name: &str) -> PathBuf {
        let directory = std::env::temp_dir().join(format!("readiness-{}", std::process::id()));
        std::fs::create_dir_all(&directory).unwrap();
        directory.join(name)
    }

    fn read(path: &std::path::Path) -> String {
        std::fs::read_to_string(path).unwrap()
    }

    #[tokio::test]
    async fn status_file_follows_the_state() {
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

    #[tokio::test(start_paused = true)]
    async fn deadline_counts_from_the_first_not_ready() {
        let readiness = Readiness::new(status_file("first"), "mqtt: connecting");
        tokio::time::advance(Duration::from_secs(60)).await;
        readiness.not_ready("mqtt: connection refused");

        let started = Instant::now();
        let line = readiness.deadline(Duration::from_secs(120)).await;
        assert_eq!(started.elapsed(), Duration::from_secs(60));
        assert!(line.starts_with("not ready: mqtt: connection refused since "));
    }

    #[tokio::test(start_paused = true)]
    async fn ready_restarts_the_deadline() {
        let readiness = Readiness::new(status_file("restart"), "mqtt: connecting");
        let watcher = readiness.clone();
        let deadline =
            tokio::spawn(async move { watcher.deadline(Duration::from_secs(120)).await });

        tokio::time::sleep(Duration::from_secs(100)).await;
        readiness.ready("mqtt connected");
        tokio::time::sleep(Duration::from_secs(100)).await;
        assert!(!deadline.is_finished());

        readiness.not_ready("mqtt: connection reset");
        let started = Instant::now();
        deadline.await.unwrap();
        assert!(started.elapsed() >= Duration::from_secs(120));
    }

    #[test]
    fn utc_clock_formats_the_time_of_day() {
        let time = UNIX_EPOCH + Duration::from_secs(3 * 86_400 + 13 * 3600 + 2 * 60 + 5);
        assert_eq!(utc_clock(time), "13:02:05");
    }
}
