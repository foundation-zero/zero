import { describe, expect, it } from "vitest";
import { parseStateDiagram, planEdges, stateDiagramProblem } from "./state-diagram.utils";

const PVT = `stateDiagram-v2
  direction LR

  state "Idle" as idle
  idle : <b>On entry</b>
  idle : • set the mix valve to 20 %
  idle : <b>On exit</b>
  idle : • start the pump

  state "Warmup" as warmup
  warmup : <b>On entry</b>
  warmup : • run the pump at the group's minimum duty point

  state "Recovery" as recovery

  [*] --> idle
  idle --> warmup : the warmest string temperature rises<br/>above recovery_activation_string_temperature
  warmup --> recovery : the mix valve<br/>opens beyond 20 %
  recovery --> warmup : the mix valve<br/>closes below 5 %
  warmup --> idle : the return falls below<br/>minimum_return_temperature
  recovery --> idle : the return falls below<br/>minimum_return_temperature

  class idle Idle
  class warmup BoostingLow
  class recovery Using`;

describe("parseStateDiagram", () => {
  it("reads the states, their entry and exit actions, and the transitions", () => {
    const diagram = parseStateDiagram(PVT)!;

    expect(diagram.initial).toBe("idle");
    expect(diagram.states.map(({ id }) => id)).toEqual(["idle", "warmup", "recovery"]);
    expect(diagram.states[0]).toEqual({
      id: "idle",
      title: "Idle",
      mode: "Idle",
      sections: [
        { heading: "On entry", items: ["set the mix valve to 20 %"] },
        { heading: "On exit", items: ["start the pump"] },
      ],
    });
    expect(diagram.transitions[0]).toEqual({
      from: "idle",
      to: "warmup",
      label: [
        "the warmest string temperature rises",
        "above recovery_activation_string_temperature",
      ],
    });
  });

  it("puts the initial state first", () => {
    const diagram = parseStateDiagram(`stateDiagram-v2
  state "A" as a
  state "B" as b
  [*] --> b
  b --> a`)!;

    expect(diagram.states.map(({ id }) => id)).toEqual(["b", "a"]);
  });

  it.each([
    ["a nested state", 'state "A" as a {', 'unsupported line "state "A" as a {"'],
    ["a final state", "a --> [*]", 'a final state, "a --> [*]"'],
    ["a transition to itself", "a --> a", "a transition from a to itself"],
    ["a note", "note right of a : x", 'unsupported line "note right of a : x"'],
  ])("leaves a diagram with %s to Mermaid, and says why", (_, line, problem) => {
    const source = `stateDiagram-v2\n  ${line}`;
    expect(parseStateDiagram(source)).toBeUndefined();
    expect(stateDiagramProblem(source)).toBe(problem);
  });

  it("finds no problem in a diagram it draws", () => {
    expect(stateDiagramProblem(PVT)).toBeUndefined();
  });
});

describe("planEdges", () => {
  it("routes transitions as the design draws the PVT diagram", () => {
    const edges = planEdges(parseStateDiagram(PVT)!).map(
      ({ from, to, side, lane, fromPort, toPort }) => ({ from, to, side, lane, fromPort, toPort }),
    );

    expect(edges).toEqual([
      // To the right, above the states, in one lane: they do not overlap.
      { from: "idle", to: "warmup", side: "top", lane: 0, fromPort: 1 / 2, toPort: 1 / 3 },
      { from: "warmup", to: "recovery", side: "top", lane: 0, fromPort: 2 / 3, toPort: 1 / 2 },
      // To the left, below; the longest one in the outer lane, attached outermost.
      { from: "recovery", to: "warmup", side: "bottom", lane: 0, fromPort: 1 / 3, toPort: 2 / 3 },
      { from: "warmup", to: "idle", side: "bottom", lane: 0, fromPort: 1 / 3, toPort: 2 / 3 },
      { from: "recovery", to: "idle", side: "bottom", lane: 1, fromPort: 2 / 3, toPort: 1 / 3 },
    ]);
  });
});
