import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { describe, expect, it } from "vitest";
import { deserializeField, getCustomField, ModuleField, serializeField } from ".";

describe("field serialization", () => {
  const field: ModuleField = [SensorComponentType.Temperature, "thrusters", "tempIn", null];

  it("round-trips a field through its string form", () => {
    const serialized = serializeField(field);

    expect(serialized).toBe(`${SensorComponentType.Temperature}.thrusters.tempIn`);
    expect(deserializeField(serialized!)).toEqual(field.slice(0, 3));
  });

  it("leaves custom data out of the string form", () => {
    const custom = getCustomField("thrusters", { technicalName: "tag", title: "Title" });

    expect(serializeField(custom)).toBe("custom.thrusters.tag");
  });

  it.each(["", "thrusters.tempIn", "a.b.c.d"])("rejects malformed input %j", (input) => {
    expect(deserializeField(input)).toBeUndefined();
  });
});
