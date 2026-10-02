import { MimicComponentType } from "@/modules/thrapp/types";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DcPumpField = "dcPumpAft" | "dcPumpUgrid" | "dcPumpFwd";

const pump = (field: DcPumpField) => {
  const source = getField(SensorComponentType.Pump, "dc", field);
  return toInstance<MimicComponentType.Pump>({
    controls: {
      pump: getField(ControlComponentType.Pump, "dc", field),
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

export const DC_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1020": pump("dcPumpAft"),
    "1023": pump("dcPumpUgrid"),
    "1025": pump("dcPumpFwd"),
  },
});
