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

Deliverable, per module, written to `/tmp/thrs-manuals/` — manuals are not
committed to this service:

- `<module>.html` — the manual as an HTML fragment, with the Mermaid source of
  its state diagram embedded. This is what the front-end shows in its
  Documentation tab. The prose above *Tuning* stays within **425 words**; the
  parameter and alarm sections run as long as they need (see *Length* below).
- `<module>.svg` — the diagram rendered from that source in step 5. The
  front-end shows it in place of the Mermaid block; it never runs Mermaid itself.

Once it passes the checks, ask whether to publish it to the front-end (step 7).
Publishing also prints `<module>.pdf`, the manual on A4 for the crew; the PDF is
never committed.

**Refreshing a manual?** The published one is
`zero-ui/src/modules/thrapp/documentation/<module>.html`. Read it first and
carry over what is still true — in particular answers the user gave last time
about equipment and the plant, which the code cannot give you again. A refresh
usually starts from a failing `tests/manuals/test_published_manuals.py`, which
means the manual's control version is stale; if the code changed but nothing
the manual says did, `just manual_stamp <module>` re-stamps the published manual
instead. The same test fails when a published `<module>.svg` was not rendered
from its manual's current Mermaid source or from the current
`assets/diagram.css`; render and publish it again.

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

**The shipped figure** you write by hand as a Mermaid `stateDiagram-v2`, embedded
in the manual. Mermaid rather than a drawing because the next person edits text
instead of redrawing a picture; step 5 renders it to an SVG that uses the
front-end's own colour variables, which colours each state by its mode and
follows dark mode. `references/template.md` has the house style.

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
  merged label reads as nothing at all. If the labels collide, fix the layout
  (`direction`, shorter lines), not the content.
- **Check the rendered figure, don't trust the source.** Mermaid lays out the
  graph itself, and long edge labels can make it far wider than tall. Look at
  the diagram preview from step 5; switch `direction` or break label lines with
  `<br/>` if it is wider than about 4:1.

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

### Trace behaviour, do not infer it

The first reviewed manuals were wrong in the same way three times: the prose
described what the module plausibly does, not what the code does. Trace these
three kinds of claim to the line that makes them true:

- **Which way a setpoint moves things.** Read the sign of the controller's gains
  and what the actuator does physically. `simple_pid` computes setpoint minus
  measurement, so negative gains open the valve further while the measurement is
  above the setpoint. Write the direction as what the valve or pump does, then
  the consequence: "the valves open further while the return is above it, so
  lowering it recovers more heat".
- **What a switch looks at.** For "takes over when" or "switches to", find the
  function that picks the tank or source and describe the one it picks. A claim
  about "any tank" is almost always wrong.
- **When an alarm is raised.** *Raised when* says what the alarm's predicate
  checks, in physical terms. Wording in its message, like "because no other
  tank is available", is what the author expected to be true, not a condition
  the code checks.

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

The reason in that example came from the user; the code only has the value.

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

**The prose above the tuning section stays within 425 words** — the title line,
"What it does", the modes, and any text around the state diagram; the diagram
and its caption do not count. That is the part the engineer reads end to end,
and it stays short enough that they will. A word count rather than a page,
because the diagram's rendered size varies by module and says nothing about how
much there is to read. DHW, the most involved module, needs about 410.

**The tuning and alarm sections run as long as they need.** Nobody reads a
parameter reference; they look one entry up in it, so completeness beats brevity
there. Never drop a parameter to save space — a setting on the panel that
appears in no manual is worse than a long list.

Printed on A4, that lands DHW (25 parameters, 13 alarms) at about four pages
and a small module at two. If the prose is over the limit, cut the prose; do not
start trimming rows.

Still group the tuning table sensibly, because grouping tracks who touches what rather
than saving room:

- **Operating parameters** — setpoints, thresholds, enables, flows. Each gets
  its own description, with real guidance. These are what gets changed at sea.
- **Functional groups** — several parameters that only make sense together
  share one description. Each still gets its own row and default; the shared
  description spans them. DHW's four stall-guard settings get one description
  starting "Stall guard, in the order listed: …". One description the engineer
  can act on beats four they have to reassemble.
- **Controller gains** — the `*_tuning` PID triplets, in a closing *Controller
  gains* group: "proportional, integral and derivative gains for the PID
  controllers, tuned during commissioning". Do not describe them as fixed or
  factory-set, and do not invent a direction to move them in.

The grouping tracks authority, not word count: the engineer on board moves
setpoints, gain changes go through engineering. Every parameter still appears
somewhere — grouped, never omitted.

## 5. Render it

```bash
just manual <module>
```

It stamps `/tmp/thrs-manuals/<module>.html` with the control version it
describes, then renders the Mermaid block to `<module>.svg` in headless
Chromium, installing Chromium first if needed. The version is a hash of the
step-1 output and of the module's source files, sub-controls included; the SVG
carries a hash of the Mermaid source and of `assets/diagram.css` it was rendered
from. A unit test fails when either no longer matches.

The render uses the house diagram styling in `assets/diagram.css` and the
front-end's fonts, so the SVG is what the reader sees. It also writes
`<module>-diagram.png` and counts the words of prose above *Tuning* against the
limit. Look at the PNG — it is the quickest way to see the diagram as the reader
will. Render again after every change to the Mermaid block.

## 6. Check it before handing it over

- Every state, transition and parameter in the manual appears in the step-1
  output, and nothing in the figure is absent from the ground-truth diagram.
- Defaults and units in the manual match the script output exactly. A wrong
  default is worse than no manual.
- Every parameter in the step-1 output appears in the manual, on its own or
  inside a named group. Silently dropping one is how an engineer ends up with a
  setting nobody can explain. Check it rather than trusting your own reading:

  ```bash
  uv run python docs/skills/thrs-module-manual/scripts/module_facts.py <module> \
    | sed -n '/^## Parameters/,/^## Alarms/p' | grep -oE "^- [a-z0-9_]+" | sed 's/^- //' \
    | while read p; do grep -q "$p" /tmp/thrs-manuals/<module>.html || echo "MISSING: $p"; done
  ```
- Every sentence that says the module does something, or which way to move a
  parameter, points to a function in the module. Go through them one by one and
  name it; fix or cut any you cannot. A plausible sentence the code does not
  back is the most common error in a draft, and the hardest for a reader to spot.
- Every reason given for a value ("set by the rating of …", "a material limit")
  comes from the code or from the user. Ask about any that came from neither.
- The prose above *Tuning* is within 425 words. Check it rather than guessing —
  the render in step 5 counts it, and says so when the prose is too long.
- Read it once as the engineer: could you take this to the plant, find the
  parameter on the panel, and know which way to move it? If not, the tuning
  column is still restating names.

## 7. Ask whether to update the front-end

Hand over the HTML and the diagram preview, then **ask the user whether to
publish the manual to the front-end**. The Documentation tab is what the crew reads on
board, so publishing is the user's call, not a default — a draft they still want
to review, or a manual for a branch that has not shipped, must not land there.

On yes, copy the fragment and its SVG in, format the fragment with zero-ui's
Prettier, which CI checks and which leaves the Mermaid block's content as it is,
and print the PDF:

```bash
just manual_publish <module>
```

It writes `/tmp/thrs-manuals/<module>.pdf` from the manual and its SVG, printed
plainly in black and white by `assets/print.css`; hand it over for the crew.

The tab picks up every file in that directory; nothing needs registering. The
file name is the module tab it appears under (`dhw`, `pvt`, `pcm`, `thrusters`,
`adsorption`, `dc`, `drives`, or a mimic key such as `pvt-main`). A module with
no tab of its own, like `consumers`, has nowhere to appear — ask which tab it
belongs under rather than inventing a name. When it replaces a published
manual, summarise what changed in a sentence or two so the user can review the
diff knowingly.

On no, leave zero-ui untouched; the HTML and SVG stay in `/tmp/thrs-manuals/`.
