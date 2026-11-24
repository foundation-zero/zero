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

## Commits and pull requests

Do not credit Claude or any other AI tool in commit messages or PR
descriptions: no `Co-Authored-By: Claude` trailer, no "Generated with Claude
Code" line. CI rejects pull requests whose commits contain them.
