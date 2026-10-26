import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toManualValve } from "../../helpers";

const manualValveTags = [
  "1174-02",
  "1069-17",
  "1169-01",
  "1169-02",
  "1169-03",
  "1174-01",
  "1069-18",
  "1069-10",
  "1168-06",
  "1168-05",
  "1168-04",
];

export const DHW_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    manualValveTags.map((tag) => [tag, toManualValve(tag)]),
  ),
});
