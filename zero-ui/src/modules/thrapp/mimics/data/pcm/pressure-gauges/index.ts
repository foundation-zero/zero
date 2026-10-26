import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toPressureGauge } from "../../helpers";

const pressureGaugeTags = ["1095-06", "1096-09"];

export const PCM_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: Object.fromEntries(
    pressureGaugeTags.map((tag) => [tag, toPressureGauge(tag)]),
  ),
});
