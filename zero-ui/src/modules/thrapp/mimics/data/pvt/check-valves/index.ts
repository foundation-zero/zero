import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toCheckValve } from "../../helpers";

const checkValveTags = [
  "1077-01",
  "1077-02",
  "1076-01",
  "1188-01",
  "1188-02",
  "1095-05",
  "1185-01",
];

export const PVT_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(
    checkValveTags.map((tag) => [tag, toCheckValve(tag, { componentType: "3 way valve DN 25" })]),
  ),
});
