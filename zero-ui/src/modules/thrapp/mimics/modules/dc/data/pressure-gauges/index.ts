import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const pressureGauge = (yardTag: string) => {
  const source = getField(
    SensorComponentType.Pressure,
    "dc",
    "placeholder",
  ) as unknown as ModuleField<"custom", "dc">;
  return toInstance<MimicComponentType.PressureGauge>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Manual pressure sensor",
        componentType: "Manual pressure sensor",
        yardTag,
      });
    },
  });
};

export const DC_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: {
    "1095-10": pressureGauge("1095-10"),
    "1095-11": pressureGauge("1095-11"),
    "1095-12": pressureGauge("1095-12"),
    "1096-06": pressureGauge("1096-06"),
  },
});
