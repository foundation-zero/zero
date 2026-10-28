import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toPressureGauge } from "../../helpers";

const pressureGaugeTags = ["1095-07", "1096-02", "1096-01", "1095-09", "1096-07", "1096-08"];

export const ADSORPTION_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: Object.fromEntries(
    pressureGaugeTags.map((tag) => [tag, toPressureGauge(tag)]),
  ),
});
