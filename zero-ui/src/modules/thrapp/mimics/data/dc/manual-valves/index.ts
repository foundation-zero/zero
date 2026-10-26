import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toManualValve } from "../../helpers";

const manualValveTags = [
  "1168-27",
  "1168-28",
  "1168-29",
  "1168-15",
  "1168-16",
  "1169-17",
  "1069-18",
  "1067-08",
  "1067-07",
  "1172-05",
  "1172-06",
  "1170-04",
  "1170-03",
  "1167-13",
  "1068-22",
];

export const DC_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    manualValveTags.map((tag) => [tag, toManualValve(tag)]),
  ),
});
