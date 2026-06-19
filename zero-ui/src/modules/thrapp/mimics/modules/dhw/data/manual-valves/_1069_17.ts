import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  custom: {},
  parameters: {},
  source: undefined,
  sensors: {},
  tooltip: tooltip({
    yardTag: "1069-17",
    technicalName: "dhw-manual-valve-1069-17",
  }),
});
