import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type PcmSwitchValveField =
  | "placeholder"
  | "pcmSwitchChargingSupply"
  | "pcmSwitchDischarging"
  | "pcmSwitchChargingReturn"
  | "pcmSwitchConsumers";

const createSwitchValve = (yardTag: string, field: PcmSwitchValveField = "placeholder") =>
  toInstance<MimicComponentType.SwitchValve>({
    controls: { valve: getField(ControlComponentType.Valve, "pcm", field) },
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Valve, "pcm", field),
    sensors: {},
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Switch valve",
        yardTag,
        componentType: "Switch valve",
      });
    },
  });

export const PCM_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1190-01": createSwitchValve("1190-01", "pcmSwitchChargingSupply"),
    "1066-01": createSwitchValve("1066-01", "pcmSwitchDischarging"),
    "1062-02": createSwitchValve("1062-02", "pcmSwitchChargingReturn"),
    "1066-02": createSwitchValve("1066-02"),
    "1067-15": createSwitchValve("1067-15"),
    "1071-02": createSwitchValve("1071-02", "pcmSwitchConsumers"),
  },
});
