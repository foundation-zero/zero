import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const DRIVES_EXPANSION_TANK_DATA = toFieldsMap({
  [MimicComponentType.ExpansionTank]: {
    "1040-04": toInstance<MimicComponentType.ExpansionTank>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("drives", {
        yardTag: "1040-04",
        technicalName: "drives-expansion-tank-1040-04",
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
