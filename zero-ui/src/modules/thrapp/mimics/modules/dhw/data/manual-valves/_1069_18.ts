import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", "dhw-manual-valve-1069-18"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1069-18",
    technicalName: "dhw-manual-valve-1069-18",
  }),
});
