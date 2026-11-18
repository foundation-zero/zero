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
  // Converter branches, shown in the group sub-mimics
  "1067-01",
  "1067-02",
  "1067-03",
  "1067-04",
  "1067-05",
  "1067-06",
  "1168-10",
  "1168-11",
];

export const DC_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    manualValveTags.map((tag) => [tag, toManualValve(tag)]),
  ),
});
