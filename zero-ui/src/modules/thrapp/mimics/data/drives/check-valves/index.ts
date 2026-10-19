import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toCheckValve } from "../../helpers";

const checkValveTags = ["1090-01", "1090-02"];

export const DRIVES_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(
    checkValveTags.map((tag) => [tag, toCheckValve(tag)]),
  ),
});
