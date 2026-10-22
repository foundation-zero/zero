import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toPressureGauge } from "../../helpers";

const pressureGaugeTags = ["1096-05", "1095-13"];

export const DRIVES_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: Object.fromEntries(
    pressureGaugeTags.map((tag) => [tag, toPressureGauge(tag)]),
  ),
});
