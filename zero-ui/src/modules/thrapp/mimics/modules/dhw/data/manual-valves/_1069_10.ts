import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", "dhw-manual-valve-1069-10"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1069-10",
    technicalName: "dhw-manual-valve-1069-10",
  }),
});
