import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toManualValve } from "../../helpers";

const manualValveTags = [
  "1084-01",
  "1087-08",
  "1212-01",
  "1212-02",
  "1212-03",
  "1212-04",
  "1212-05",
  "1212-06",
  "1212-07",
  "1087-03",
  "1167-11",
];

export const THRUSTERS_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    manualValveTags.map((tag) => [tag, toManualValve(tag)]),
  ),
});
