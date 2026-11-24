# Agents

## Codestyle

**[CODESTYLE.md](./CODESTYLE.md)** is the single source of truth for code conventions in this repo.

It covers:
- Python
- TypeScript/Vue
- Rust
- Tooling configuration

If you are an agent tasked with writing or modifying code, **read CODESTYLE.md first** and follow its conventions. Do not introduce patterns that contradict it.

## Skills

Reusable task instructions live next to the code they describe, as a directory
holding a `SKILL.md` plus any scripts and references it needs:

- [zero-thrs-control/docs/skills/thrs-module-manual](./zero-thrs-control/docs/skills/thrs-module-manual)
  — write or refresh the functional description of a THRS control module,
  shown in the zero-ui Documentation tab and printed as a PDF for the crew.
- [docs/skills/comment-review](./docs/skills/comment-review)
  — review a service's comments one at a time and remove, reword or code away
  those that restate the code, prop up a workaround or have gone stale.

A `SKILL.md` starts with a `description` saying when it applies. Read the ones
that match your task before you start; commands in them are written to run from
the service directory (`zero-thrs-control`), not from the repository root.
