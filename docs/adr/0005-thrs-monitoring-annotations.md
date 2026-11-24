# Crew notes on THRS Monitoring are kept in GreptimeDB and owned by a browser, not a login

The crew can pin a note to a moment on the Monitoring charts. THRS has no user accounts, so the author is a name the crew types, and a note belongs to the browser that wrote it. That browser holds a random key in local storage. The server stores only the key's SHA-256 hash with the note, and deletes a note only for a request that carries the matching key. Clearing the browser's storage gives up that right.

Notes live in GreptimeDB (`thrs__monitoring__annotations`), next to the history they describe, so the monitoring API needs only one database. The parameter changes and alarms shown beside them are derived from existing tables when the page reads them, and never stored.

## Considered options

- **Require a login.** That would give real authors and permissions, but THRS has no accounts, and a shared crew tablet would need one anyway. Revisit when the yacht has single sign-on.
- **Let anyone delete any note.** The simplest option, but one mistaken tap removes someone else's note for good.
- **Store notes in thrs-control's Postgres.** It's transactional, but it is a second database for the API to reach, and the notes would sit apart from their history.
