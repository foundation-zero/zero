import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  custom: {},
  parameters: {},
  sensors: {},
  tooltip: tooltip({
    yardTag: "1169-01",
    technicalName: "boilers-manual-valve-1169-01",
  }),
});
