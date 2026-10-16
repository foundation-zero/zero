import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PVT_EXPANSION_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ExpansionValve]: {
    "1041-01": toInstance<MimicComponentType.ExpansionValve>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("pvt", {
        yardTag: "1041-01",
        technicalName: "pvt-expansion-valve-1041-01",
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
