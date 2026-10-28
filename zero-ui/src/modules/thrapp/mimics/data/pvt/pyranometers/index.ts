import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";

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
