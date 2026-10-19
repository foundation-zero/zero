import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toCheckValve } from "../../helpers";

const checkValveTags = ["1213-01", "1213-02", "1217-01", "1217-02"];

export const THRUSTERS_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(
    checkValveTags.map((tag) => [tag, toCheckValve(tag)]),
  ),
});
