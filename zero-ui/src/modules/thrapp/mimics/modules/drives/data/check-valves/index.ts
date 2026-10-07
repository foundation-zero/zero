import { getCustomField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { fieldTooltip } from "../../../shared";

const checkValve = (yardTag: string) =>
  toInstance<MimicComponentType.CheckValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getCustomField("drives", {
      yardTag,
      technicalName: `drives-check-valve-${yardTag}`,
    }),
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Check valve",
        componentType: "Check valve",
      });
    },
  });

export const DRIVES_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: {
    "1090-01": checkValve("1090-01"),
    "1090-02": checkValve("1090-02"),
  },
});
