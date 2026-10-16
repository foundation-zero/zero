import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PVT_EXPANSION_TANK_DATA = toFieldsMap({
  [MimicComponentType.ExpansionTank]: {
    "1040-01": toInstance<MimicComponentType.ExpansionTank>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("pvt", {
        yardTag: "1040-01",
        technicalName: "pvt-expansion-tank-1040-01",
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
