import { describe, expect, test } from "vitest";
import { formatUnit, getDeflectionDisplayName } from "./utils";

describe("getDeflectionDisplayName", () => {
  test.each([
    ["fiber-optic-main-mast-fa-deflection100", "100% Height"],
    ["fiber-optic-mizzen-mast-sw-deflection050", "50% Height"],
    ["fiber-optic-main-mast-sw-deflection000", "0% Height"],
    ["fiber-optic-main-mast-fa-deflection-spr3", "Spreader 3"],
    ["fiber-optic-main-d1-ps", null],
  ])("'%s' is shown as '%s'", (variableId, expected) => {
    expect(getDeflectionDisplayName(variableId)).toBe(expected);
  });
});

describe("formatUnit", () => {
  const t = (key: string) => `<${key}>`;

  test("translates known API units", () => {
    expect(formatUnit("deg_c", t)).toBe("<rig.units.degC>");
  });

  test("passes unknown units through", () => {
    expect(formatUnit("bar", t)).toBe("bar");
  });

  test("returns an empty string without a unit", () => {
    expect(formatUnit(null, t)).toBe("");
  });
});
