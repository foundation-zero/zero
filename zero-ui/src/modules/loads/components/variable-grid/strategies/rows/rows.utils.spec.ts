import { describe, expect, test, vi } from "vitest";
import { createBrokenRowGroups, createUnbrokenRowGroups } from ".";
import type { VariableGroup } from "../../../../lib/consts.dashboards";
import { PositionId, Variable, VariableUnit } from "../../../../types";

// getGridSize depends on reactive breakpoints (window size), so we mock it to a fixed value
vi.mock("../..", async (importOriginal) => {
  const original = await importOriginal<typeof import("../..")>();
  return { ...original, getGridSize: vi.fn().mockReturnValue(3) };
});

const makeVariable = (id: string, unit: VariableUnit = VariableUnit.Ratio): Variable => ({
  id,
  reference: { target: 0 },
  variable: {
    id,
    name: id,
    unit,
    scaleMin: 0,
    scaleMax: 1,
    scaleMinLabel: null,
    scaleMaxLabel: null,
  },
  actual: { id, value: 0 },
});

const makeGroup = (
  name: string,
  position: PositionId,
  variables: Variable[] = [],
): VariableGroup<Variable> => ({
  name,
  position,
  variables,
  includeInDynamic: false,
});

describe("createUnbrokenRowGroups", () => {
  test("returns an empty array when given no groups", () => {
    expect(createUnbrokenRowGroups([], 3)).toEqual([]);
  });

  test("returns one GridGroup per input group", () => {
    const groups = [
      makeGroup("A", PositionId.Main, [makeVariable("v1")]),
      makeGroup("B", PositionId.ForeInner, [makeVariable("v2")]),
    ];

    expect(createUnbrokenRowGroups(groups, 3)).toHaveLength(2);
  });

  test("assigns gridSize as the size of each GridGroup", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("v1")]);

    const [result] = createUnbrokenRowGroups([group], 6);

    expect(result.size).toBe(6);
  });

  test("preserves all variables from the original group", () => {
    const v1 = makeVariable("v1");
    const v2 = makeVariable("v2");
    const group = makeGroup("A", PositionId.Main, [v1, v2]);

    const [result] = createUnbrokenRowGroups([group], 3);

    expect(result.variables).toEqual([v1, v2]);
  });

  test("references the original VariableGroup on the group property", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("v1")]);

    const [result] = createUnbrokenRowGroups([group], 3);

    expect(result.group).toBe(group);
  });

  test("sets hasBooleans to true when a group contains a Bool variable", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("bv", VariableUnit.Bool)]);

    const [result] = createUnbrokenRowGroups([group], 3);

    expect(result.hasBooleans).toBe(true);
  });

  test("sets hasBooleans to false when no Bool variable is present", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("v1")]);

    const [result] = createUnbrokenRowGroups([group], 3);

    expect(result.hasBooleans).toBe(false);
  });
});

describe("createBrokenRowGroups", () => {
  // getGridSize is mocked to return 3; getItemSize("numerical") returns 1 per non-Bool variable

  test("returns an empty array when given no groups", () => {
    expect(createBrokenRowGroups([], "numerical")).toEqual([]);
  });

  test("returns a single GridGroup when all variables fit within the row", () => {
    const group = makeGroup("A", PositionId.Main, [
      makeVariable("v1"),
      makeVariable("v2"),
      makeVariable("v3"),
    ]);

    expect(createBrokenRowGroups([group], "numerical")).toHaveLength(1);
  });

  test("splits a group into multiple GridGroups when variables overflow the row", () => {
    const group = makeGroup("A", PositionId.Main, [
      makeVariable("v1"),
      makeVariable("v2"),
      makeVariable("v3"),
      makeVariable("v4"),
    ]);

    // gridSize=3: row 0 gets v1–v3, row 1 gets v4
    expect(createBrokenRowGroups([group], "numerical")).toHaveLength(2);
  });

  test("assigns the correct variables to each sub-group after splitting", () => {
    const v1 = makeVariable("v1");
    const v2 = makeVariable("v2");
    const v3 = makeVariable("v3");
    const v4 = makeVariable("v4");
    const group = makeGroup("A", PositionId.Main, [v1, v2, v3, v4]);

    const [first, second] = createBrokenRowGroups([group], "numerical");

    expect(first.variables).toEqual([v1, v2, v3]);
    expect(second.variables).toEqual([v4]);
  });

  test("size of each sub-group equals the sum of its variable sizes", () => {
    const group = makeGroup("A", PositionId.Main, [
      makeVariable("v1"),
      makeVariable("v2"),
      makeVariable("v3"),
      makeVariable("v4"),
    ]);

    const [first, second] = createBrokenRowGroups([group], "numerical");

    expect(first.size).toBe(3);
    expect(second.size).toBe(1);
  });

  test("every sub-group references the original VariableGroup", () => {
    const group = makeGroup("A", PositionId.Main, [
      makeVariable("v1"),
      makeVariable("v2"),
      makeVariable("v3"),
      makeVariable("v4"),
    ]);

    for (const subGroup of createBrokenRowGroups([group], "numerical")) {
      expect(subGroup.group).toBe(group);
    }
  });

  test("continues packing variables from a subsequent group into remaining row space", () => {
    // groupA uses 2 of 3 slots in row 0
    // groupB's first variable fills the last slot in row 0; second wraps to row 1
    const groupA = makeGroup("A", PositionId.Main, [makeVariable("v1"), makeVariable("v2")]);
    const groupB = makeGroup("B", PositionId.ForeInner, [makeVariable("v3"), makeVariable("v4")]);

    const result = createBrokenRowGroups([groupA, groupB], "numerical");

    // groupA → 1 sub-group (v1, v2); groupB → 2 sub-groups (v3 | v4)
    expect(result).toHaveLength(3);
    expect(result[0].group).toBe(groupA);
    expect(result[1].group).toBe(groupB);
    expect(result[2].group).toBe(groupB);
  });

  test("sets hasBooleans to true when a sub-group contains a Bool variable", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("bv", VariableUnit.Bool)]);

    const [result] = createBrokenRowGroups([group], "numerical");

    expect(result.hasBooleans).toBe(true);
  });

  test("sets hasBooleans to false when no Bool variable is in the sub-group", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("v1")]);

    const [result] = createBrokenRowGroups([group], "numerical");

    expect(result.hasBooleans).toBe(false);
  });
});
