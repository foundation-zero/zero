import { describe, expect, test } from "vitest";
import { parseSchema, parseSchemaNested } from "./thrs";

describe("THRS Store", () => {
  describe("schemas", () => {
    test("it parses unnested fields correctly", async () => {
      const schema = {
        $defs: {
          Celsius: { minimum: -273.15, type: "number" },
        },
        properties: {
          cooling_mix_setpoint: { $ref: "#/$defs/Celsius", default: 38 },
        },
        title: "ThrustersParameters",
        type: "object",
      };

      const parsed = await parseSchema(schema);
      expect(parsed[0]).to.include({
        name: "cooling_mix_setpoint",
        default: 38,
        description: undefined,
        maximum: undefined,
        minimum: -273.15,
      });

      const object = {};
      const result = parsed[0].set(object, 40);
      expect(result).toEqual({ cooling_mix_setpoint: 40 });
      expect(parsed[0].get(result)).toEqual(40);
    });

    test("it parses nested fields correctly", async () => {
      const a = {
        $defs: {
          Stamp_Watt_: {
            $ref: "#/$defs/Stamped_Watt_",
          },
          Stamp_bool_: {
            $ref: "#/$defs/Stamped_bool_",
          },
          Stamped_Watt_: {
            properties: {
              value: {
                $ref: "#/$defs/Watt",
              },
              timestamp: {
                format: "date-time",
                title: "Timestamp",
                type: "string",
              },
            },
            required: ["value", "timestamp"],
            title: "Stamped[Watt]",
            type: "object",
          },
          Stamped_bool_: {
            properties: {
              value: {
                title: "Value",
                type: "boolean",
              },
              timestamp: {
                format: "date-time",
                title: "Timestamp",
                type: "string",
              },
            },
            required: ["value", "timestamp"],
            title: "Stamped[bool]",
            type: "object",
          },
          Thruster: {
            properties: {
              heat_flow: {
                $ref: "#/$defs/Stamp_Watt_",
              },
              active: {
                $ref: "#/$defs/Stamp_bool_",
              },
            },
            required: ["heat_flow", "active"],
            title: "Thruster",
            type: "object",
          },
          Watt: {
            type: "number",
          },
        },
        additionalProperties: false,
        properties: {
          thrusters_aft: {
            $ref: "#/$defs/Thruster",
          },
        },
        required: ["thrusters_aft"],
        title: "ThrustersSimulationInputs",
        type: "object",
      };

      const parsed = await parseSchemaNested(a);

      expect(parsed[0].name).toBe("thrusters_aft");
      expect(parsed[0].fields[0].name).toBe("heat_flow");
      expect(parsed[0].fields[0].type).toBe("number");
      expect(parsed[0].fields[1].name).toBe("active");
      expect(parsed[0].fields[1].type).toBe("boolean");
      const object = {};
      const result = parsed[0].fields[0].set(object, 100);
      expect(result).toEqual({
        thrusters_aft: { heat_flow: { value: 100, timestamp: expect.any(String) } },
      });
      expect(parsed[0].fields[0].get(result)).toEqual(100);
    });
  });
});
