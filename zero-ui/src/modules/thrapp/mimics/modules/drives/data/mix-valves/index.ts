import { MimicComponentType } from "@/modules/thrapp/types";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DrivesMixValveField = "drivesMixExchanger" | "drivesMixRecovery";

const mixValve = (field: DrivesMixValveField) => {
  const source = getField(SensorComponentType.Valve, "drives", field);
  return toInstance<MimicComponentType.MixValve>({
    controls: {
      valve: getField(ControlComponentType.Valve, "drives", field),
    },
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Mix valve",
        componentType: "3 way valve DN 25",
      });
    },
  });
};

export const DRIVES_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1046-01": mixValve("drivesMixExchanger"),
    "1046-03": mixValve("drivesMixRecovery"),
  },
});
