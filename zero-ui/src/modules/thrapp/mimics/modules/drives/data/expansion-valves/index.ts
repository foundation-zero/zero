import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const DRIVES_EXPANSION_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ExpansionValve]: {
    "1041-05": toInstance<MimicComponentType.ExpansionValve>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("drives", {
        yardTag: "1041-05",
        technicalName: "drives-expansion-valve-1041-05",
      }),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Pressure valve",
          componentType: "Pressure valve",
        });
      },
    }),
  },
});
