---
name: thrs-module-manual
description: >-
  Write the functional description ("manual") for a zero-thrs-control control
  module — what the module is for, how its control logic behaves, the state
  diagram, and how each parameter can be tuned — aimed at the engineer on
  board who tests and operates the system, not at a developer. Use this whenever
  the user asks for a manual, functional description, operating description,
  write-up or hand-over documentation for a named control module (dhw, pvt, pcm,
  thrusters, adsorption, consumers, dc, drives), or asks to refresh an existing
  one after the control logic changed. Use it even for a module that looks
  simple, because the facts are extracted from the live code by a bundled script
  rather than read off the source, which is what keeps the manual true.
---

# THRS control module manuals

A manual explains one module of the THRS plant to the **engineer on board** who
commissions, tests and operates it. They know pumps, valves, heat and °C. They do
not read Python, and they will not have the repository open. The manual is the
bridge between the control code and the person standing in front of the hardware.

Deliverable, per module:

- `zero-thrs-control/docs/manuals/<module>.md` — prose fits **one page**; the
  parameter and alarm tables run as long as they need (see *Length* below)
- `zero-thrs-control/docs/manuals/figures/<module>-states.dot` and `.png`
- on request, a PDF or DOCX rendered from the markdown

## 1. Extract the facts

Never read the parameter list, transition table or alarm codes off the source by
eye — that is exactly where a manual quietly goes stale. Run:

```bash
cd zero-thrs-control
uv run python docs/skills/thrs-module-manual/scripts/module_facts.py <module> \
  --diagram /tmp/<module>-truth.png
```

It prints, from the live objects: every parameter with its unit, default, real
bounds and in-code description; the cross-parameter validators; alarm codes and
severities; **the control modes the operator sees**; the actuators and sensors;
and each state machine with its `on_enter`/`on_exit` hooks and transition
conditions (lambdas included, as source). `--diagram` writes the raw
pytransitions rendering.

If the script reports the module has no `*_MODULE_DESCRIPTION`, it is a helper
like `converters` or `pvt_group` — it belongs inside its parent's manual, not in
one of its own.

## 2. Read for intent

The script gives you *what* the module does. It cannot tell you *why*, and the
why is most of the manual's value. Read `src/thrs/control/modules/<module>.py`
and its tests under `tests/modules/<module>/` for:

- What physical job the module has, what it is trying to maximise or protect,
  and when it is expected to run at all.
- What each controller regulates, and against which measurement — a PID on a
  mixing valve chasing a return temperature is a sentence the engineer needs.
- Why a state exists. `boosting` is not "a state"; it is "heating a full tank
  from the high-temperature loop because the tank fell below its minimum".
- **Where the heat comes from and where it goes.** A module is a stage in a
  circuit, and its neighbours are rarely named in its own file. Trace them, and
  use the circuit's mimic name — PVT delivers recovered heat to the *high
  temperature circuit*, and only the seawater cooler is an *exchanger*. Getting
  this wrong misplaces the module in the plant, which is worse than leaving it
  vague. If you cannot establish it from the code, ask (below).
- **Designed degraded behaviour** — what happens when the heat, water or flow it
  needs is not there, *where the control has an actual response to it*: a
  fallback selection, a mode it drops to, an alarm. DHW serving the warmest
  remaining tank and raising a warning is designed behaviour and belongs in the
  manual.

  Defensive coding is not. A null-check that skips a sensor with no reading, a
  guard against a missing value — these are implementation detail, and writing
  them up ("a group whose string sensor reads nothing stays idle") presents an
  unhandled edge case as though it were intended behaviour. If the control does
  not do something deliberate about the case, the manual is silent on it.

The `control()` method read top to bottom tells you the order of operations in a
tick, which is usually the clearest spine for the "How it works" paragraph.

### Modes deserve particular care

The **mode** is what the operator reads off the panel as "what the control is
doing right now", so it is one of the first things the manual must pin down. Two
traps:

- A module can report **several independent mode dimensions** — DHW has a
  filling mode and a boosting mode, PVT one per group. Name each dimension and
  list its values.
- **Not every mode comes from the state machine.** DHW's filling mode is derived
  from the tank controller, not from a state. The distinction matters to you
  while writing and not at all to the reader: they see two modes either way, so
  describe both the same way and never mention where the value came from.

Step 1 prints the mode dimensions and the source of the `mode` property so you
can see which values are possible and how each is derived.

## 3. The diagram

Two diagrams, one shipped.

**Ground truth** is the `--diagram` PNG from step 1. It is generated from the
live machine, so it is correct by construction, but it is labelled with method
names. Do not ship it — redraw it.

**Redraw it, do not simplify it.** The thing that makes the generated diagram
useful is exactly what a prettified version tends to throw away: each state
listing what it *does* on entry and exit, and each edge carrying the *condition*
that fires it. Keep both. Translate `_set_valves_to_boosting_heatpump` into
"open the heatpump source valve", not into nothing. A box with only a name in it
has lost the engineering content and is not worth the space it takes.

**The shipped figure** you write by hand as Graphviz, at
`docs/manuals/figures/<module>-states.dot`, then render:

```bash
dot -Tpng -Gdpi=150 docs/manuals/figures/<module>-states.dot \
  -o docs/manuals/figures/<module>-states.png
```

Graphviz rather than Mermaid because the PNG embeds in GitHub markdown *and*
survives the pandoc export to PDF/DOCX, which a Mermaid fence does not. Keep the
`.dot` in version control so the next person edits a diagram instead of redrawing
one. `references/template.md` has the house style.

Before shipping, compare the two pictures state by state and edge by edge. Same
states, same transitions, same direction. If your figure is missing an edge, the
engineer will one day watch the plant do something the manual says is impossible.

When a module runs several identical machines — PVT has one per group — draw it
once and say in the caption that each group runs it independently. Drawing three
copies of the same two-state machine tells the reader nothing and costs a third
of the page.

Three things that come up nearly every time:

- **Unreachable states.** A module may define a state nothing transitions into
  (DHW's low-temperature boosting). Leave it out of the figure *and* out of the
  text. Documenting what is not implemented costs space and invites the reader to
  wait for behaviour that will never come.
- **Two states that swap back and forth.** Keep them as two separate arrows with
  their own conditions — the conditions are different in each direction, and a
  merged `dir=both` arrow forces a vague joint label that reads as nothing at
  all. If the two labels collide, fix the layout (`rankdir`, `nodesep`, shorter
  lines), not the content.
- **Check the aspect ratio, don't eyeball it.** `dot` will happily emit
  something 5:1 that is unreadable once scaled to the page width. Measure, and
  switch `rankdir` if it is wider than about 4:1.

```bash
python3 -c "import struct; d=open('figures/<module>-states.png','rb').read(33); \
w,h=struct.unpack('>II',d[16:24]); print(f'{w}x{h} ratio={w/h:.2f}')"
```

Scale the figure down where it is embedded, or it takes the full text width and
with it half the page — which is what pushes the prose onto a second page:

```markdown
![<Module> operating states](figures/<module>-states.png){width=55%}
```

## 4. Write it

Follow the skeleton in `references/template.md`. The sections are fixed so an
engineer who has read one manual can find their way around any of them.

### Writing for this reader

The reader is a **marine engineer**, not a layperson. They are not fluent in
Python; they are entirely fluent in temperatures, flows, valves and setpoints.
Aim for the register of a commissioning document: technical, precise, dry. The
failure mode to guard against is not "too difficult" — it is **plain-language
paraphrase that drops the number**.

- **Name the quantity and the threshold.** Not "when the loop is hot enough to
  give it", but "when the supply is more than `ht_boosting_minimum_delta` above
  the tank". Not "checks heat is genuinely reaching the tank", but "checks heat
  transfer stays above `boosting_minimum_heat`". If a sentence describes a
  condition, the condition's actual quantity belongs in it.
- **No code identifiers, but parameter names are not code.** Method and class
  names (`_ht_boosting_available`, `TanksController`) never appear. Parameter
  names do, verbatim and often — they are the labels on the panel, and naming
  one is how the reader connects a sentence to something they can change.
- **Use the system's own vocabulary.** If the control calls the tank states
  *needs fill*, *needs boost*, *standby*, use those words rather than inventing
  a paraphrase like "each tank has one job". Invented vocabulary reads as
  approximate and will not match the mimic in front of them.
- **Name hardware the way the mimic names it.** The component name gives the
  type: `*_switch_*` is a **switch valve**, `*_mix_*` a **mix valve** (the
  three-way), `*_flowcontrol_*` a **flow control valve**. Never invent a
  descriptive substitute — and never reach for "manual", which in this system
  means a hand-operated valve (the mimic legend lists "manual switch valve"
  separately from "switch valve"). Calling a remotely actuated valve "manual"
  names the wrong equipment.
- **Name the action, not a metaphor.** "Disables heatpump boosting", not "locks
  out the heatpump". "The high-temperature supply drops below the margin", not
  "the loop falls away". Metaphor is where precision goes to die.
- **Nothing anthropomorphic and nothing chatty.** The module is not *patient*,
  does not *give way*, does not find a source *worth using*. Cut "genuinely",
  "actually", "simply".
- **State and value in physical terms.** "The pump runs at a duty point set by a
  PID chasing 70 °C on the return line", not "the pump controller is enabled".
  "Charging stops" is weaker than "the charging valves close and the pump stops".

### Never write a fact you did not read

Everything in the manual is checkable against the module. Do not add provenance
("factory-set", "set by the yard"), prohibitions ("never lower this below…"),
or trade-offs you have not verified in the code or been told. An invented
prohibition is worse than silence: it stops an engineer doing something
legitimate, and it costs you their trust in the rest of the page. If the reason
for a value is not in the code, either leave it unexplained or ask — see below.

Present tense, active voice, no hedging throughout. This is an operating
description; where behaviour is conditional, name the condition.

### Tuning guidance

This is the half of the manual the engineer comes back to. **Match the depth of
the entry to the parameter** — the common failure is writing every row as if it
were a control-strategy decision. Three kinds:

**A setpoint with a real trade-off** gets the full treatment: what it means,
then what you gain and give up by moving it.

> `recovery_activation_string_temperature` — 40 °C. The string temperature above
> which the group starts circulating. Raise it to stop the pumps short-cycling on
> a cold bright morning; lower it to start harvesting earlier on marginal days.

**A value fixed by the equipment** gets one clause naming what fixes it. Pump
and exchanger flow setpoints usually come from a datasheet, not from a control
trade-off, and inventing a trade-off for them is worse than saying nothing:

> `heatpump_flow_setpoint` — 25 l/min. Boosting loop flow from the heatpump, set
> by the heatpump's rated flow.

**A guard or floor** gets one clause saying what it protects:

> Minimum valve and pump openings — floors that guarantee flow through the
> system, so the temperature sensors read the circulating medium.

"Controls the activation temperature" restates the name and is worth nothing;
but so is a fabricated trade-off. When you cannot tell which kind a parameter is
from the code, ask (below) rather than guess.

Carry across the **hard constraints** from the model validators in words: "must
stay above the warm-up temperature, or the module refuses the settings". An
engineer whose parameter change is silently rejected has no way to diagnose that
from the panel.

### Ask about what the code cannot tell you

A parameter's *value* is in the code; the *reason for that value* often is not.
Whether 25 l/min is a heat-exchanger rating, a commissioning result or an
arbitrary starting point changes what the manual should say, and nothing in the
module distinguishes them.

Before writing the tuning section, gather the parameters whose rationale you
cannot source and **ask the user in one batch** — a short list of specific
questions beats either guessing or interrupting repeatedly. Worth asking about:

- **Where the module sits in the plant** — which circuit feeds it, which circuit
  receives what it produces, and what each named piece of equipment on its
  boundary actually is. This is the highest-value question on the list: the
  module's own file names its valves and sensors but almost never says what is
  on the other side of them, and a manual that misplaces the module in the
  system is wrong in a way the reader cannot correct.
- Flow and temperature setpoints that look like equipment ratings.
- Thresholds with suspiciously round values, which are often placeholders.
- Anything where you are about to write "raise it to…" without knowing what
  raising it costs.

Their answers are facts you could not otherwise have; fold them in directly.

### Length

**Everything above the tuning section fits on one page** — the title line, "What
it does", the modes, and the state diagram. That is the part the engineer reads
end to end, and it stays short enough that they will.

**The tuning and alarm sections run as long as they need.** Nobody reads a
parameter reference; they look one entry up in it, so completeness beats brevity
there. Never drop a parameter to save space — a setting on the panel that
appears in no manual is worse than a long list.

Measured on A4 at 1.8 cm margins, that lands DHW (25 parameters, 13 alarms) at
about four pages and a small module at one or two. If the prose alone is
overrunning, cut the prose; do not start trimming rows.

Still group the table sensibly, because grouping tracks who touches what rather
than saving room:

- **Operating parameters** — setpoints, thresholds, enables, flows. One row
  each, with real guidance. These are what gets changed at sea.
- **Functional groups** — several parameters that only make sense together get
  one row under a name, with the defaults listed in order. DHW's four stall-guard
  settings become "Stall guard: `boosting_minimum_heat`, `boosting_stall_window`,
  `boosting_startup_grace`, `boosting_stall_cooldown` | 1000 W, 120 s, 180 s,
  900 s | how patient the module is with a boost that is not delivering…". One
  row the engineer can act on beats four they have to reassemble.
- **Controller gains** — the `*_tuning` PID triplets, all in a single closing
  entry: "gains for the PID controllers (proportional, integral, derivative)".
  They are tuned during commissioning, so do not describe them as fixed or
  factory-set, and do not invent a direction to move them in.

The grouping tracks authority, not word count: the engineer on board moves
setpoints, gain changes go through engineering. Every parameter still appears
somewhere — grouped, never omitted.

## 5. Export on request

```bash
cd zero-thrs-control/docs/manuals
pandoc <module>.md -o <module>.pdf     # PDF via LaTeX
pandoc <module>.md -o <module>.docx    # DOCX, no engine needed
```

Run pandoc from the manuals directory so the relative `figures/` path resolves.
Exported files are build artifacts — do not commit them unless asked.

## 6. Check it before handing it over

- Every state, transition and parameter in the manual appears in the step-1
  output, and nothing in the figure is absent from the ground-truth diagram.
- Defaults and units in the table match the script output exactly. A wrong
  default is worse than no manual.
- Every parameter in the step-1 output appears in the manual, on its own or
  inside a named group. Silently dropping one is how an engineer ends up with a
  setting nobody can explain. Check it rather than trusting your own reading:

  ```bash
  cd zero-thrs-control
  uv run python docs/skills/thrs-module-manual/scripts/module_facts.py <module> \
    | sed -n '/^## Parameters/,/^###/p' | grep -oE "^- [a-z0-9_]+" | sed 's/^- //' \
    | while read p; do grep -q "$p" docs/manuals/<module>.md || echo "MISSING: $p"; done
  ```
- The prose above the tuning table fits one page. Check it rather than guessing
  — markdown length is a poor guide once tables and a figure are involved:

  ```bash
  cd zero-thrs-control/docs/manuals
  pandoc <module>.md -o /tmp/<module>.pdf -V geometry:a4paper -V geometry:margin=1.8cm
  pdfinfo /tmp/<module>.pdf | grep Pages
  ```
- Read it once as the engineer: could you take this to the plant, find the
  parameter on the panel, and know which way to move it? If not, the tuning
  column is still restating names.
