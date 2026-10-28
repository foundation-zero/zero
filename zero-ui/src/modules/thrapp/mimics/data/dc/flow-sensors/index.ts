import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

export const DC_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-25": toFlowSensor({
      source: getField(SensorComponentType.Flow, "dc", "dcFlowAftReturn"),
    }),
    "1057-26": toFlowSensor({
      source: getField(SensorComponentType.Flow, "dc", "dcFlowFwdReturn"),
    }),
    "1058-06": toFlowSensor({
      source: getField(SensorComponentType.Flow, "dc", "dcFlowUgridReturn"),
    }),
    "1058-04": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowRecovery") }),
  },
});
