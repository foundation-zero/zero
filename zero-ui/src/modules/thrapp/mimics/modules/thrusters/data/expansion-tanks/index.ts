import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const THRUSTERS_EXPANSION_TANK_DATA = toFieldsMap({
  [MimicComponentType.ExpansionTank]: {
    "1092": toInstance<MimicComponentType.ExpansionTank>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("thrusters", {
        yardTag: "1092",
        technicalName: "thrusters-expansion-tank-1092",
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
