import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PCM_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1017": toInstance<MimicComponentType.Pump>({
      custom: {},
      controllerState: {},
      source: getField(SensorComponentType.Pump, "pcm", "pcmPump"),
      controls: {
        pump: getField(ControlComponentType.Pump, "pcm", "pcmPump"),
      },
      parameters: {},
      sensors: {},
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Pump",
          yardTag: "1017",
          componentType: "Circulation pump",
        });
      },
    }),
  },
});
