import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DcPressureField = "dcPressureAft" | "dcPressureUgrid" | "dcPressureFwd";

const pressureTooltip = (field: ModuleField<SensorComponentType.Pressure, "dc">): TooltipContent =>
  fieldTooltip(field, {
    title: "Pressure sensor",
    componentType: "Pressure sensor",
  });

const pressureSensor = (field: DcPressureField) => {
  const source = getField(SensorComponentType.Pressure, "dc", field);
  return toInstance<MimicComponentType.PressureSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return pressureTooltip(this.source);
    },
  });
};

export const DC_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-07": pressureSensor("dcPressureAft"),
    "1097-08": pressureSensor("dcPressureUgrid"),
    "1097-09": pressureSensor("dcPressureFwd"),
  },
});
