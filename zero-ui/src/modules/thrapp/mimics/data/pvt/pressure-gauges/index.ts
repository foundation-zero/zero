import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toPressureGauge } from "../../helpers";

const pressureGaugeTags = ["1095-03", "1095-04", "1188-03"];

export const PVT_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: Object.fromEntries(
    pressureGaugeTags.map((tag) => [tag, toPressureGauge(tag)]),
  ),
});
