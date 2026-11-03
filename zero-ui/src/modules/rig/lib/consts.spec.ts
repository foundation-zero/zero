import { describe, expect, test } from "vitest";
import { RIG_COLUMNS } from "./consts";
import { RIG_VARIABLE_IDS } from "./consts.variables";

describe("RIG_COLUMNS", () => {
  const layoutIds = RIG_COLUMNS.flatMap((column) =>
    column.cards.flatMap((card) => card.rows.flatMap((row) => row.variableIds)),
  );

  test("only uses known rig variable ids", () => {
    expect(RIG_VARIABLE_IDS).toEqual(expect.arrayContaining(layoutIds));
  });

  test("shows every rig variable id", () => {
    expect(new Set(layoutIds)).toEqual(new Set(RIG_VARIABLE_IDS));
  });
});
