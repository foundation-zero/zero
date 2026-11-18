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
    "1057-04": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowAft4") }),
    "1057-05": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowAft3") }),
    "1057-06": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowAft2") }),
    "1057-07": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowAft1") }),
    "1057-08": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowUgrid2") }),
    "1057-09": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowUgrid1") }),
    "1057-11": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowFwd2") }),
    "1057-12": toFlowSensor({ source: getField(SensorComponentType.Flow, "dc", "dcFlowFwd1") }),
  },
});
