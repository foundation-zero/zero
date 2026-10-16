import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const DC_EXPANSION_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ExpansionValve]: {
    "1041-06": toInstance<MimicComponentType.ExpansionValve>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("dc", {
        yardTag: "1041-06",
        technicalName: "dc-expansion-valve-1041-06",
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
