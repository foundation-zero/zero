import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PVT_PYRANOMETER_DATA = toFieldsMap({
  [MimicComponentType.Pyranometer]: {
    "9044": toInstance<MimicComponentType.Pyranometer>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getField(SensorComponentType.Pyranometer, "pvt", "pvtPyranometerSb"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Pyranometer",
          componentType: "Pyranometer",
        });
      },
    }),
    "9043": toInstance<MimicComponentType.Pyranometer>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getField(SensorComponentType.Pyranometer, "pvt", "pvtPyranometerPs"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Pyranometer",
          componentType: "Pyranometer",
        });
      },
    }),
  },
});
