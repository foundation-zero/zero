import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

// Flow sensors of the PVT owners strings.
export const PVT_OWNERS_FLOW_SENSORS = {
  "9009-07": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString1"),
  }),
  "9009-08": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString2"),
  }),
  "9009-09": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString3"),
  }),
  "9009-10": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString4"),
  }),
  "9009-11": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString5"),
  }),
  "9009-12": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString6"),
  }),
};
