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

A `SKILL.md` starts with a `description` saying when it applies. Read the ones
that match your task before you start; commands in them are written to run from
the service directory (`zero-thrs-control`), not from the repository root.

## Agent skills

### Issue tracker

Issues live in Jira project ZERO (foundationzero-team.atlassian.net), reached through the Atlassian MCP tools (setup in the same doc). See `docs/agents/issue-tracker.md`.

### Triage labels

Optional: the five default triage roles as plain Jira labels, only when triage is asked for. See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context: `GLOSSARY-MAP.md` at the root points at per-service glossaries; system-wide ADRs live in `docs/adr/`, service-scoped ones in `<service>/docs/adr/`. See `docs/agents/domain.md`.
