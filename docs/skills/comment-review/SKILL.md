---
name: comment-review
description: Review every comment in a service, one at a time, and remove, reword or code away the ones that restate the code, prop up a workaround or have gone stale.
disable-model-invocation: true
---

# Comment review

Go through every comment in a scope (usually one service), decide per comment
whether it earns its place, and change it with the user one comment at a time.
A comment earns its place by saying **why**: what the code cannot say. The
interesting finds are rarely the restatements; they are the **crutches**, where
the comment explains around code that should change, and the **stale** ones,
whose reason no longer holds.

Commands run from the service directory. Changes go on a new branch from
`main`; commit only when the user asks.

## Steps

### 1. Inventory

List every comment in scope, trailing ones included, with one `rg`, leaving
out pragmas (`noqa`, `pyrefly: ignore`, `type:`, `fmt:`, `ruff:`):

    rg -n -A2 --pcre2 '(^|\s)#(?![!:])(?! (type|pyrefly|noqa|fmt|ruff))' --type py src tests

Cover the source, tests, analysis and scripts. Done when every comment line is
in the list.

### 2. Investigate each comment

Read the code around the comment, then answer three questions. Done for a
comment when all three have an answer backed by something you read or ran.

- **Is it true?** Check each claim the comment makes against the code and its
  consumers: grep the dependency it blames (is it still in `pyproject.toml`?),
  the service it names (does it still exist?), the reader it protects (who reads
  this field now?). Test a claim about a library by running a three-line
  snippet. Comments in this repo went stale when Strawberry and thrs-api left.
- **What does it explain around?** Duplicated branches, positional `{}`
  arguments, a magic number, a hand-kept ignore list, a reshape the library
  can do (`squeeze=False`), an unused function. Name the code change that would
  make the comment unnecessary.
- **What would a reader lose without it?** A why that lives nowhere else
  (a hardware quirk, a protocol limit, a physical constant, why QoS 0) stays.

### 3. Classify

- **Restatement**: says what the next line says. Delete it.
- **Crutch**: explains around a smell. Propose the code change; the comment goes
  with it. Prefer a better name over a comment (a test named after what it
  verifies, a parameter named after what it holds).
- **Stale**: its reason no longer holds. Delete it, and propose removing the
  workaround it justified when that is now dead too.
- **Why**: keep it. Reword only a typo, a garbled sentence or a long trailing
  comment that belongs above its statement.

### 4. Ask, one comment per question

Use the question tool. Order: restatements first, then crutches, stale
comments, and the keeps last.

- **One comment per question**, even when several look alike; at most four
  questions per call.
- **The question stands alone**: the comment's text, its file and line, and in
  one sentence why you classify it so.
- **The preview is a unified diff** with the repo-relative path, real line
  numbers and about six lines of context on each side. Describe instead of
  diffing when a change spans more than ten lines or several places.
- **Options**: Keep, Remove, Chat.

On **Chat**, dig further before answering: read the consumers, run the claim,
look at what the comment's neighbours depend on. Come back with what you found
and two or three options with a recommendation. A Chat answer turned up the
best changes in the session this skill came from.

### 5. Apply and recheck

Apply each accepted change with an edit right after the answer. After a batch,
reread the deletions: a deleted comment can leave a misleading name behind
(a parameter called `non_fmu_simulation_inputs` that also gets outputs), and
the honest fix is then the rename.

### 6. Verify

Done when all of these hold:

- the service's `just check` passes, formatting
  included, also for scripts outside `src` and `tests`;
- generated artifacts (AsyncAPI spec, generated UI definitions) are regenerated
  and either unchanged or their change is explained to the user;
- a failing manual fingerprint is restamped only after checking the manual
  still describes the code;

## Calibration

How this repo's owner decided, as a starting point for your recommendations:

- **Kept**: section labels and test banners, even where a name prefix repeats
  them; TODOs, whose conditions are for the domain owner to change; commented-out
  reference code; scenario comments in tests; every why.
- **Removed**: restatements and step narration, template leftovers, reasons that
  name a removed dependency or service, a claim shown false.
- **Preferred**: a renamed test over a `# Verifies …` comment; a code fix over a
  reworded crutch; facts you verified over a reason you inferred. Reword a TODO
  or a reason only with a condition you can point to in code.
