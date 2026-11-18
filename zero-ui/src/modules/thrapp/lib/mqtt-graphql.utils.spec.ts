import { describe, expect, it } from "vitest";
import { MQTT_GRAPHQL_DEFINITIONS } from "./definitions.generated";
import { toThrsModules } from "./mqtt-graphql.utils";

const stamped = (value: unknown) => ({ value, timestamp: "2026-11-11T15:08:32.961981Z" });

describe("toThrsModules", () => {
  it("places each component at its module and part, from its path in the response", () => {
    const modules = toThrsModules({
      marpower: {
        _500000Thrs: {
          dhw: { dhwPump: { flow: stamped(0.5) } },
          consumers: { consumersFlowDhw: { flow: stamped(2) } },
        },
      },
      thrs: {
        controller: {
          dhw: {
            controlValues: { dhwPump: { dutypoint: stamped(0.1), on: stamped(true) } },
            dhwTanksController: { tank1State: stamped("NEEDS_FILL") },
            parameters: { maximumTankTemperature: 60 },
          },
        },
      },
    });

    expect(modules.dhw).toEqual({
      sensorValues: { dhwPump: { flow: stamped(0.5) } },
      controlValues: { dhwPump: { dutypoint: stamped(0.1), on: stamped(true) } },
      controllerState: { dhwTanksController: { tank1State: stamped("NEEDS_FILL") } },
      parameters: { maximumTankTemperature: 60 },
    });
    expect(modules.consumers.sensorValues).toEqual({ consumersFlowDhw: { flow: stamped(2) } });
  });

  it("knows modules of other systems and components with digit groups", () => {
    const modules = toThrsModules({
      marpower: {
        _250000FreshWater: { hot: { hotFlowToPcm: { flow: stamped(1) } } },
        _500000Thrs: { pvt: { pvtFlowMainString1_1: { flow: stamped(3) } } },
      },
    });

    expect(modules.freshWaterHot.sensorValues).toEqual({ hotFlowToPcm: { flow: stamped(1) } });
    expect(modules.pvt.sensorValues).toEqual({ pvtFlowMainString1_1: { flow: stamped(3) } });
  });

  it("ignores components that are not in the definitions", () => {
    const modules = toThrsModules({
      marpower: {
        _500000Thrs: { dhw: { notADhwComponent: { flow: stamped(1) } } },
        _340000Sewage: { grey: { greyLevel: { level: stamped(1) } } },
      },
    });

    expect(modules.dhw).toEqual({});
    expect(modules).not.toHaveProperty("sewageGrey");
  });

  it("has every defined module, with the parts the query selected, empty without a value", () => {
    const modules = toThrsModules({
      marpower: { _500000Thrs: { dhw: { dhwPump: null } } },
      thrs: { controller: { dhw: { controlValues: null, parameters: null } } },
    });

    expect(Object.keys(modules)).toEqual(Object.keys(MQTT_GRAPHQL_DEFINITIONS));
    expect(modules.dhw).toEqual({ sensorValues: {}, controlValues: {}, parameters: {} });
    expect(modules.pcm).toEqual({});
  });
});
