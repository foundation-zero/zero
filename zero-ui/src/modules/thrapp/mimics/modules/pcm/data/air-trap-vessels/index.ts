import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PCM_AIR_TRAP_VESSEL_DATA = toFieldsMap({
  [MimicComponentType.AirTrapVessel]: {
    "1084": toInstance<MimicComponentType.AirTrapVessel>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("pcm", {
        yardTag: "1084",
        technicalName: "pcm-air-trap-vessel-1084",
      }),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Air trap vessel",
          componentType: "Air trap vessel",
        });
      },
    }),
  },
});
