import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toCheckValve } from "../../helpers";

const checkValveTags = ["1078-01", "1085-02"];

export const PCM_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(
    checkValveTags.map((tag) => [tag, toCheckValve(tag)]),
  ),
});
