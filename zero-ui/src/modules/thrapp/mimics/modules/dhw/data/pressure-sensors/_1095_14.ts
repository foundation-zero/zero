import { getCustomField } from "@/modules/thrapp/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.PressureGauge>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", "dhw-manual-pressure-sensor-1095-14"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1095-14",
    technicalName: "dhw-manual-pressure-sensor-1095-14",
    title: "Manual pressure sensor",
    itemName: "Manual pressure sensor",
  }),
});
