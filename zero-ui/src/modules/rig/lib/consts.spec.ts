import { describe, expect, test } from "vitest";
import { RIG_MASTS } from "./consts";
import { RIG_VARIABLE_IDS } from "./consts.variables";

describe("RIG_MASTS", () => {
  test("shows exactly the rig variable ids", () => {
    const layoutIds = RIG_MASTS.flatMap((mast) =>
      mast.cards.flatMap((card) => card.rows.flatMap((row) => row.variableIds)),
    );

    expect(new Set(layoutIds)).toEqual(new Set(RIG_VARIABLE_IDS));
  });
});
