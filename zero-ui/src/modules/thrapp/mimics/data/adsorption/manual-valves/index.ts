import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toManualValve } from "../../helpers";

const manualValveTags = [
  "1170-02",
  "1171-01",
  "1171-02",
  "1073-01",
  "1073-02",
  "1072-01",
  "1072-02",
  "1072-03",
  "1072-04",
  "1170-08",
  "1167-12",
  "1168-21",
  "1175",
  "1168-20",
];

export const ADSORPTION_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    manualValveTags.map((tag) => [tag, toManualValve(tag)]),
  ),
});
