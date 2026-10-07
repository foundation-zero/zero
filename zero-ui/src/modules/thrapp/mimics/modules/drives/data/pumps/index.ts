import { MimicComponentType } from "@/modules/thrapp/types";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DrivesPumpField = "drivesPump1" | "drivesPump2";

const pump = (field: DrivesPumpField) => {
  const source = getField(SensorComponentType.Pump, "drives", field);
  return toInstance<MimicComponentType.Pump>({
    controls: {
      pump: getField(ControlComponentType.Pump, "drives", field),
    },
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Pump",
        componentType: "Pump",
      });
    },
  });
};

export const DRIVES_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1028": pump("drivesPump1"),
    "1029": pump("drivesPump2"),
  },
});
