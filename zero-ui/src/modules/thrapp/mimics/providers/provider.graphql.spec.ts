import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { DocumentNode, print } from "graphql";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reactive, ref } from "vue";
import { ModuleField } from ".";
import { MimicComponentState } from "../components";
import { useGraphQLDataProvider } from "./provider.graphql";

const history = reactive({
  data: undefined as unknown,
  refresh: vi.fn(),
  mutate: vi.fn(),
});
const automaticMode = ref<boolean | undefined>(true);
const advisoryEnabled = ref<boolean | null>(true);

vi.mock("@/modules/thrapp/stores/history", () => ({
  useThrsHistory: () => history,
}));

vi.mock("../../state", () => ({
  useAutomaticMode: () => automaticMode,
  useAdvisoryEnabled: () => advisoryEnabled,
}));

const stamp = <T>(value: T) => ({ value, timestamp: new Date() });
const lastMutation = () => {
  const [query, variables] = history.mutate.mock.lastCall as [DocumentNode, { input: unknown }];
  return { query: print(query), input: variables.input };
};

describe("GraphQL mimic data provider", () => {
  beforeEach(() => {
    history.data = undefined;
    history.refresh.mockReset().mockResolvedValue(undefined);
    history.mutate.mockReset().mockResolvedValue({});
    automaticMode.value = true;
    advisoryEnabled.value = true;
  });

  describe("reading values", () => {
    it("warns once when the loaded data lacks a module part that is read", () => {
      const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
      history.data = { modules: { thrusters: { controlValues: {} } } };
      const provider = useGraphQLDataProvider();
      const field = [SensorComponentType.Temperature, "thrusters", "tempIn", null] as const;

      expect(provider.getSensorValue([...field]).value).toBeUndefined();
      expect(provider.getSensorValue([...field]).value).toBeUndefined();

      expect(warn).toHaveBeenCalledOnce();
      expect(warn.mock.calls[0][0]).toContain('"thrusters.sensorValues"');
      warn.mockRestore();
    });

    it("reads each kind of field from its own section of the module", () => {
      const sensor = { temperature: stamp(20) };
      const control = { dutypoint: stamp(0.5) };
      const controllerState = { setpoint: stamp(55) };
      history.data = {
        modules: {
          thrusters: {
            sensorValues: { tempIn: sensor },
            controlValues: { pump: control },
            parameters: { coolingTemperature: 60 },
            controllerState: { pid: controllerState },
          },
        },
      };
      const provider = useGraphQLDataProvider();

      expect(
        provider.getSensorValue([SensorComponentType.Temperature, "thrusters", "tempIn", null])
          .value,
      ).toEqual(sensor);
      expect(
        provider.getControlValue([ControlComponentType.Pump, "thrusters", "pump", null]).value,
      ).toEqual(control);
      expect(
        provider.getParameter([ParametersType.Temperature, "thrusters", "coolingTemperature", null])
          .value,
      ).toBe(60);
      expect(
        provider.getControllerState([
          ControllerStateComponentType.PIDController,
          "thrusters",
          "pid",
          null,
        ]).value,
      ).toEqual(controllerState);
    });

    it("updates when new data arrives", () => {
      const parameter = useGraphQLDataProvider().getParameter([
        ParametersType.Temperature,
        "thrusters",
        "coolingTemperature",
        null,
      ]);
      expect(parameter.value).toBeUndefined();

      history.data = { modules: { thrusters: { parameters: { coolingTemperature: 65 } } } };

      expect(parameter.value).toBe(65);
    });
  });

  describe("setting a parameter", () => {
    const source: ModuleField<ParametersType.Temperature> = [
      ParametersType.Temperature,
      "thrusters",
      "coolingTemperature",
      null,
    ];

    it("sends the parameter in the module controller's parameters, then refreshes", async () => {
      await useGraphQLDataProvider().setParameter(source, 62);

      const { query, input } = lastMutation();
      expect(query).toContain("mutation ($input: ThrsControlThrustersParametersInput!)");
      expect(query).toContain("thrusters {");
      expect(query).toContain("parameters(input: $input)");
      expect(input).toEqual({ coolingTemperature: 62 });
      expect(history.refresh).toHaveBeenCalledOnce();
    });

    it("rejects a module without a controller, without sending anything", async () => {
      await expect(
        useGraphQLDataProvider().setParameter(
          [ParametersType.Temperature, "cooling", "placeholder", null],
          60,
        ),
      ).rejects.toThrow("cooling has no controller");
      expect(history.mutate).not.toHaveBeenCalled();
    });

    it("refreshes and then throws when the mutation fails", async () => {
      const error = new Error("Out of range");
      history.mutate.mockResolvedValue({ error });

      await expect(useGraphQLDataProvider().setParameter(source, 999)).rejects.toBe(error);
      expect(history.refresh).toHaveBeenCalledOnce();
    });
  });

  describe("setting a control value", () => {
    it("sends the values stamped with now in the module controller's control values", async () => {
      vi.setSystemTime(new Date("2026-11-11T12:00:00Z"));
      const timeStamp = "2026-11-11T12:00:00.000Z";

      await useGraphQLDataProvider().setControlValue(
        [ControlComponentType.Pump, "thrusters", "thrustersPump1", null],
        { dutypoint: 0.8, on: true, __typename: "Pump" } as never,
      );

      const { query, input } = lastMutation();
      expect(query).toContain("mutation ($input: ThrsControlThrustersControlValuesInput!)");
      expect(query).toContain("controlValues(input: $input)");
      expect(input).toEqual({
        thrustersPump1: { dutypoint: { value: 0.8, timeStamp }, on: { value: true, timeStamp } },
      });
      expect(history.refresh).toHaveBeenCalledOnce();
      vi.useRealTimers();
    });
  });

  describe("component state", () => {
    it.each([
      { advisory: false, automatic: true, state: MimicComponentState.Alarm, expected: "normal" },
      { advisory: true, automatic: false, state: MimicComponentState.Alarm, expected: "manual" },
      { advisory: true, automatic: true, state: MimicComponentState.Alarm, expected: "alarm" },
      { advisory: true, automatic: true, state: undefined, expected: "normal" },
    ])(
      "is $expected when advisory=$advisory, automatic=$automatic and the component is $state",
      ({ advisory, automatic, state, expected }) => {
        advisoryEnabled.value = advisory;
        automaticMode.value = automatic;

        expect(useGraphQLDataProvider().getComponentState(state).value).toBe(expected);
      },
    );
  });
});
