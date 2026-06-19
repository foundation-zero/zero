import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: undefined,
  tooltip: tooltip({
    yardTag: "1174-01",
    technicalName: "dhw-manual-valve-1174-01",
  }),
});
