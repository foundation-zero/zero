import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getCustomField("dhw", "dhw-manual-valve-1174-02"),
  tooltip: tooltip({
    yardTag: "1174-02",
    technicalName: "dhw-manual-valve-1174-02",
  }),
});
