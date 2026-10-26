import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toCheckValve } from "../../helpers";

const checkValveTags = ["1076-03", "1077-04", "1075-01", "1077-03", "1075-06", "1076-02"];

export const DC_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(
    checkValveTags.map((tag) => [tag, toCheckValve(tag)]),
  ),
});
