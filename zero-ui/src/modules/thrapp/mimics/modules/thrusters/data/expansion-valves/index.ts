import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const THRUSTERS_EXPANSION_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ExpansionValve]: {
    "1041-04": toInstance<MimicComponentType.ExpansionValve>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getCustomField("thrusters", {
        yardTag: "1041-04",
        technicalName: "thrusters-expansion-valve-1041-04",
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
