import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Switch valve",
  itemName: "2 way valve DN 25",
  yardTag,
  technicalName,
});

export const THRUSTERS_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1091-01": toInstance<MimicComponentType.SwitchValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "thrusters", "thrustersSwitchAft"),
      },
      controllerState: {},
      custom: {},
      parameters: {},
      source: getField(SensorComponentType.Valve, "thrusters", "thrustersSwitchAft"),
      sensors: {},
      tooltip: tooltip("1091-01", "thrusters-switch-aft"),
    }),
    "1091-02": toInstance<MimicComponentType.SwitchValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "thrusters", "thrustersSwitchFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {},
      source: getField(SensorComponentType.Valve, "thrusters", "thrustersSwitchFwd"),
      sensors: {},
      tooltip: tooltip("1091-02", "thrusters-switch-fwd"),
    }),
    "1066-03": toInstance<MimicComponentType.SwitchValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "thrusters", "thrustersSwitchRecovery"),
      },
      controllerState: {},
      custom: {},
      parameters: {},
      source: getField(SensorComponentType.Valve, "thrusters", "thrustersSwitchRecovery"),
      sensors: {},
      tooltip: tooltip("1066-03", "thrusters-switch-recovery"),
    }),
  },
});
