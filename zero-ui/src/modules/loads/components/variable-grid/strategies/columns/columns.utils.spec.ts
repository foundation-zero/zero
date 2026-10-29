import { describe, expect, test } from "vitest";
import {
  createColumnPartitions,
  createFixedColumnGroups,
  createSmartColumnGroups,
  getColumnWidthCombinations,
  getHighestColumnRowCount,
  getSymmetricColumnSpans,
  MIN_COLUMN_SIZE,
  type ColumnPartitions,
} from ".";
import type { VariableGroup } from "../../../../lib/consts.dashboards";
import { PositionId, SailPositionGroup, Variable, VariableUnit } from "../../../../types";
import { NUMERIC_GRID_SIZE } from "../../consts";

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

const makePositionGroup = (positions: PositionId[]): SailPositionGroup => ({
  name: "group",
  positions: positions.map((position) => ({ position, sails: [] })),
});

describe("createColumnLayoutInput", () => {
  const positionGroups = [
    makePositionGroup([PositionId.Main]),
    makePositionGroup([PositionId.ForeInner]),
    makePositionGroup([PositionId.ForeOuter]),
  ];

  test("places groups into the correct position column", () => {
    const groupA = makeGroup("A", PositionId.Main, [makeVariable("v1")]);
    const groupB = makeGroup("B", PositionId.ForeInner, [makeVariable("v2")]);
    const groupC = makeGroup("C", PositionId.ForeOuter, [makeVariable("v3")]);

    const [start, center, end] = createColumnPartitions([groupA, groupB, groupC], positionGroups);

    expect(start).toContain(groupA);
    expect(center).toContain(groupB);
    expect(end).toContain(groupC);
  });

  test("returns an empty array for a column with no matching groups", () => {
    const groupA = makeGroup("A", PositionId.Main, [makeVariable("v1")]);

    const [, center, end] = createColumnPartitions([groupA], positionGroups);

    expect(center).toHaveLength(0);
    expect(end).toHaveLength(0);
  });

  test("combines multiple groups assigned to the same position into one column", () => {
    const groupA = makeGroup("A", PositionId.Main, [makeVariable("v1")]);
    const groupB = makeGroup("B", PositionId.Main, [makeVariable("v2")]);

    const [start] = createColumnPartitions([groupA, groupB], positionGroups);

    expect(start).toContain(groupA);
    expect(start).toContain(groupB);
  });

  test("combines groups from multiple positions within the same position column", () => {
    const positionGroupsWithTwo = [
      makePositionGroup([PositionId.Main]),
      makePositionGroup([PositionId.ForeInner, PositionId.ForeOuter]),
      makePositionGroup([PositionId.Mizzen]),
    ];
    const groupA = makeGroup("A", PositionId.ForeInner, [makeVariable("v1")]);
    const groupB = makeGroup("B", PositionId.ForeOuter, [makeVariable("v2")]);

    const [, center] = createColumnPartitions([groupA, groupB], positionGroupsWithTwo);

    expect(center).toHaveLength(2);
  });
});

describe("getSymmetricColumnSpans", () => {
  test("returns equal start and end spans", () => {
    const [start, , end] = getSymmetricColumnSpans(6);

    expect(start).toBe(end);
  });

  test("assigns extra column width to the center column when gridSize is odd", () => {
    const [start, center, end] = getSymmetricColumnSpans(7);

    expect(center).toBeGreaterThan(start);
    expect(center).toBeGreaterThan(end);
  });

  test("returns [2, 2, 2] for gridSize 6 (lg)", () => {
    expect(getSymmetricColumnSpans(NUMERIC_GRID_SIZE.lg)).toEqual([2, 2, 2]);
  });

  test("returns [1, 2, 1] for gridSize 4 (md)", () => {
    expect(getSymmetricColumnSpans(NUMERIC_GRID_SIZE.md)).toEqual([1, 2, 1]);
  });

  test("returns [3, 4, 3] for gridSize 10 (2xl)", () => {
    expect(getSymmetricColumnSpans(NUMERIC_GRID_SIZE["2xl"])).toEqual([3, 4, 3]);
  });

  test.each(Object.values(NUMERIC_GRID_SIZE))("column spans sum to gridSize %i", (gridSize) => {
    const [start, center, end] = getSymmetricColumnSpans(gridSize);

    expect(start + center + end).toBe(gridSize);
  });
});

describe("getColumnWidthCombinations", () => {
  test("returns one combination for gridSize 3 (sm)", () => {
    expect(getColumnWidthCombinations(NUMERIC_GRID_SIZE.sm)).toHaveLength(1);
  });

  test("returns [1, 1, 1] as the only combination for gridSize 3 (sm)", () => {
    expect(getColumnWidthCombinations(NUMERIC_GRID_SIZE.sm)).toEqual([[1, 1, 1]]);
  });

  test("returns 3 combinations for gridSize 4 (md)", () => {
    expect(getColumnWidthCombinations(NUMERIC_GRID_SIZE.md)).toHaveLength(3);
  });

  test("every combination sums to gridSize", () => {
    for (const [start, center, end] of getColumnWidthCombinations(NUMERIC_GRID_SIZE.lg)) {
      expect(start + center + end).toBe(NUMERIC_GRID_SIZE.lg);
    }
  });

  test("every column width is at least MIN_COLUMN_SIZE", () => {
    for (const [start, center, end] of getColumnWidthCombinations(NUMERIC_GRID_SIZE.lg)) {
      expect(start).toBeGreaterThanOrEqual(MIN_COLUMN_SIZE);
      expect(center).toBeGreaterThanOrEqual(MIN_COLUMN_SIZE);
      expect(end).toBeGreaterThanOrEqual(MIN_COLUMN_SIZE);
    }
  });

  test("returns an empty array when gridSize is too small for three minimum-size columns", () => {
    expect(getColumnWidthCombinations(2)).toHaveLength(0);
  });
});

describe("getHighestColumnRowCount", () => {
  test("returns 0 when all columns are empty", () => {
    const input: ColumnPartitions = [[], [], []];

    expect(getHighestColumnRowCount(input)([1, 1, 1])).toBe(0);
  });

  test("returns the row count when variables fit exactly in the column width", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("v1"), makeVariable("v2")]);
    const input: ColumnPartitions = [[group], [], []];

    expect(getHighestColumnRowCount(input)([2, 1, 1])).toBe(1);
  });

  test("applies ceil when variables do not divide evenly by column width", () => {
    const group = makeGroup("A", PositionId.Main, [
      makeVariable("v1"),
      makeVariable("v2"),
      makeVariable("v3"),
    ]);
    const input: ColumnPartitions = [[group], [], []];

    expect(getHighestColumnRowCount(input)([2, 1, 1])).toBe(2);
  });

  test("returns the maximum row count across all columns", () => {
    const groupA = makeGroup("A", PositionId.Main, [makeVariable("v1")]);
    const groupB = makeGroup("B", PositionId.ForeInner, [
      makeVariable("v2"),
      makeVariable("v3"),
      makeVariable("v4"),
    ]);
    const input: ColumnPartitions = [[groupA], [groupB], []];

    expect(getHighestColumnRowCount(input)([1, 1, 1])).toBe(3);
  });

  test("wider columns yield fewer rows for the same group", () => {
    const variables = Array.from({ length: 4 }, (_, i) => makeVariable(`v${i}`));
    const group = makeGroup("A", PositionId.Main, variables);
    const input: ColumnPartitions = [[group], [], []];

    expect(getHighestColumnRowCount(input)([1, 1, 1])).toBe(4);
    expect(getHighestColumnRowCount(input)([4, 1, 1])).toBe(1);
  });
});

describe("createFixedColumnGroups", () => {
  test("returns exactly 3 column groups", () => {
    const result = createFixedColumnGroups([[], [], []], NUMERIC_GRID_SIZE.lg);

    expect(result).toHaveLength(3);
  });

  test("assigns symmetric column spans as sizes — [2, 2, 2] for gridSize 6 (lg)", () => {
    const [start, center, end] = createFixedColumnGroups([[], [], []], NUMERIC_GRID_SIZE.lg);

    expect(start.size).toBe(2);
    expect(center.size).toBe(2);
    expect(end.size).toBe(2);
  });

  test("assigns asymmetric symmetric spans — [1, 2, 1] for gridSize 4 (md)", () => {
    const [start, center, end] = createFixedColumnGroups([[], [], []], NUMERIC_GRID_SIZE.md);

    expect(start.size).toBe(1);
    expect(center.size).toBe(2);
    expect(end.size).toBe(1);
  });

  test("places groups in the correct column", () => {
    const groupA = makeGroup("A", PositionId.Main, [makeVariable("v1")]);
    const groupB = makeGroup("B", PositionId.ForeInner, [makeVariable("v2")]);

    const [start, center] = createFixedColumnGroups([[groupA], [groupB], []], NUMERIC_GRID_SIZE.lg);

    expect(start.groups[0].group).toBe(groupA);
    expect(center.groups[0].group).toBe(groupB);
  });

  test("sets hasBooleans to true when a group contains a Bool variable", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("bv", VariableUnit.Bool)]);

    const [start] = createFixedColumnGroups([[group], [], []], NUMERIC_GRID_SIZE.lg);

    expect(start.groups[0].hasBooleans).toBe(true);
  });

  test("sets hasBooleans to false when no Bool variable is present", () => {
    const group = makeGroup("A", PositionId.Main, [makeVariable("v1")]);

    const [start] = createFixedColumnGroups([[group], [], []], NUMERIC_GRID_SIZE.lg);

    expect(start.groups[0].hasBooleans).toBe(false);
  });
});

describe("createSmartColumnGroups", () => {
  test("selects the column combination that minimizes the highest row count", () => {
    // gridSize=4 (md) → combinations: [1,1,2], [1,2,1], [2,1,1]
    const group = makeGroup("A", PositionId.Main, [makeVariable("v1"), makeVariable("v2")]);
    const input: ColumnPartitions = [[group], [], []];

    const [start, center, end] = createSmartColumnGroups(input, NUMERIC_GRID_SIZE.md);

    expect(start.size).toBe(2);
    expect(center.size).toBe(1);
    expect(end.size).toBe(1);
  });

  test("picks the first combination when multiple combinations share the same best score", () => {
    // All columns are empty → all combinations score 0 → first combination wins
    // gridSize=4 (md) → first combination is [1,1,2]
    const [start, center, end] = createSmartColumnGroups([[], [], []], NUMERIC_GRID_SIZE.md);

    expect(start.size).toBe(1);
    expect(center.size).toBe(1);
    expect(end.size).toBe(2);
  });

  test("falls back to fixed column groups when no valid combination exists", () => {
    // gridSize=2 → getColumnWidthCombinations returns [] → fallback to createFixedColumnGroups
    const [start, center, end] = createSmartColumnGroups([[], [], []], 2);

    expect(start.size).toBe(1);
    expect(center.size).toBe(0);
    expect(end.size).toBe(1);
  });
});
