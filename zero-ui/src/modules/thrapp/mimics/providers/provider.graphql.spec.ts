import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";
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

vi.mock("@/modules/thrsim/stores/history", () => ({
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

    it("sends the module's parameter mutation with the typed input, then refreshes", async () => {
      await useGraphQLDataProvider().setParameter(source, 62);

      const { query, input } = lastMutation();
      expect(query).toContain("mutation ($input: Float!)");
      expect(query).toContain("thrustersParameterSetCoolingTemperature(value: $input)");
      expect(input).toBe(62);
      expect(history.refresh).toHaveBeenCalledOnce();
    });

    it("uses a list input type for tuning parameters", async () => {
      await useGraphQLDataProvider().setParameter(
        [ParametersType.Tuning, "thrusters", "aftTemperatureTuning", null],
        [1, 0.1, 0],
      );

      expect(lastMutation().query).toContain("mutation ($input: [Float!]!)");
    });

    it("refreshes and then throws when the mutation fails", async () => {
      const error = new Error("Out of range");
      history.mutate.mockResolvedValue({ error });

      await expect(useGraphQLDataProvider().setParameter(source, 999)).rejects.toBe(error);
      expect(history.refresh).toHaveBeenCalledOnce();
    });
  });

  describe("setting a control value", () => {
    it("sends the module's control mutation without the GraphQL typename", async () => {
      await useGraphQLDataProvider().setControlValue(
        [ControlComponentType.Pump, "thrusters", "pump", null],
        { dutypoint: 0.8, on: true, __typename: "Pump" } as never,
      );

      const { query, input } = lastMutation();
      expect(query).toContain("mutation ($input: PumpInputType!)");
      expect(query).toContain("thrustersControlSetPump(value: $input)");
      expect(input).toEqual({ dutypoint: 0.8, on: true, __typename: undefined });
      expect(history.refresh).toHaveBeenCalledOnce();
    });

    it("rejects control types that have no input type, without sending anything", async () => {
      await expect(
        useGraphQLDataProvider().setControlValue(
          [ControlComponentType.Pcm, "thrusters", "pcm", null],
          { on: true },
        ),
      ).rejects.toThrow(`No input type defined for control type ${ControlComponentType.Pcm}`);
      expect(history.mutate).not.toHaveBeenCalled();
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
