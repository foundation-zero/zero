import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {},
  custom: {},
  parameters: {},
  sensors: {
    flow: getField(SensorComponentType.Flow, "boilers", "boilersFlowBoosting"),
  },
  tooltip: tooltip({
    yardTag: "1058-11",
    technicalName: "boilers-flow-boosting",
  }),
});
