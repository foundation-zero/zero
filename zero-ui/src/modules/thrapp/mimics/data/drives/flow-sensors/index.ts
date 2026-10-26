import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

export const DRIVES_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-16": toFlowSensor({
      source: getField(SensorComponentType.Flow, "drives", "drivesFlowPropdriveAft2"),
    }),
    "1057-13": toFlowSensor({
      source: getField(SensorComponentType.Flow, "drives", "drivesFlowPropdriveAft1"),
    }),
    "1057-14": toFlowSensor({
      source: getField(SensorComponentType.Flow, "drives", "drivesFlowPropdriveFwd2"),
    }),
    "1057-15": toFlowSensor({
      source: getField(SensorComponentType.Flow, "drives", "drivesFlowPropdriveFwd1"),
    }),
    "1057-10": toFlowSensor({
      source: getField(SensorComponentType.Flow, "drives", "drivesFlowShorepower"),
    }),
    "1058-03": toFlowSensor({
      source: getField(SensorComponentType.Flow, "drives", "drivesFlowRecovery"),
    }),
  },
});
