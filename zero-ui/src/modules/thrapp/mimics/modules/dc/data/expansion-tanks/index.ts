import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const DC_EXPANSION_TANK_DATA = toFieldsMap({
  [MimicComponentType.ExpansionTank]: {
    "1040-05": toInstance<MimicComponentType.ExpansionTank>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("dc", {
        yardTag: "1040-05",
        technicalName: "dc-expansion-tank-1040-05",
      }),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Expansion tank",
          componentType: "Expansion tank",
        });
      },
    }),
  },
});
