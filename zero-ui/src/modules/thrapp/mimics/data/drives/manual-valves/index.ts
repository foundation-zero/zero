import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toManualValve } from "../../helpers";

const manualValveTags = [
  "1087-04",
  "1087-05",
  "1087-06",
  "1087-07",
  "1085-04",
  "1085-05",
  "1085-02",
  "1085-03",
  "1086-01",
  "1086-02",
  "1086-09",
  "1086-10",
  "1086-06",
  "1086-05",
  "1086-07",
  "1086-08",
  "1084-02",
  "1087-01",
  "1073-02",
  "1073-01",
];

export const DRIVES_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    manualValveTags.map((tag) => [tag, toManualValve(tag)]),
  ),
});
