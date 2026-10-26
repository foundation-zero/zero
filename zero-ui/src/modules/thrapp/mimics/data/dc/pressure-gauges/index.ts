import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toPressureGauge } from "../../helpers";

const pressureGaugeTags = ["1095-10", "1095-11", "1095-12", "1096-06"];

export const DC_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: Object.fromEntries(
    pressureGaugeTags.map((tag) => [tag, toPressureGauge(tag)]),
  ),
});
