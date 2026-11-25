# Issue tracker: Jira

Issues and specs for this repo live in Jira project **ZERO** on
foundationzero-team.atlassian.net, reached through the Atlassian MCP server.
GitHub (foundation-zero/zero) holds the code and pull requests, not issues.

**Setup**: enable the Atlassian connector on claude.ai, or run
`claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp`
and sign in through `/mcp`. Without it, ask the user to create or update the
ticket instead.

## Conventions

- **Create**: type `Taak` in ZERO, with one area label (`DataPlatform`, `THRS`,
  `SailPerformance`, …). Ask for the area label, parent epic and sprint when
  they aren't clear from context.
- **Close**: comment why, then move it to the done status, or to the cancelled
  status when it won't be actioned.
- **Statuses**: names are localized per user (Dutch or English), so filter on
  `statusCategory` in JQL and choose transitions by meaning, not by name.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a Jira issue in ZERO as above.

## When a skill says "fetch the relevant ticket"

Read the Jira issue by its key (`ZERO-1234`).

## Wayfinding operations

Wayfinder work stays off the board's top level: the board holds refined issues
linked to deliverables.

- **Map**: a `Story` labelled `wayfinder:map` (plus the area label), holding the
  map body, under the epic it refines. For a large new feature or product,
  create the epic first; the map is its first ticket. As decisions resolve,
  the implementation tickets are created in that epic.
- **Child ticket**: a `Subtaak` of the map, labelled `wayfinder:<type>`; never a
  triage label.
- **Blocking**: a "Blocks" issue link from blocker to child. A ticket is
  unblocked when every blocker is in the done category.
- **Frontier**: `parent = <map> AND statusCategory != Done AND assignee is EMPTY ORDER BY rank`,
  then drop tickets with an "is blocked by" link to an issue that isn't done
  (JQL can't see the blocker's status). The first remaining one wins.
- **Claim**: assign it to the person driving the map and move it to in progress.
- **Resolve**: comment the answer, move it to done, then add a pointer to the
  map's Decisions-so-far.
- **Out of scope**: move the ticket to cancelled, not done.
