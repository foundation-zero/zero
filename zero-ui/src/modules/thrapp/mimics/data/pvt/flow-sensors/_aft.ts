import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

// Flow sensors of the PVT AFT strings.
export const PVT_AFT_FLOW_SENSORS = {
  "9006-01": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString1_1"),
  }),
  "9006-02": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString1_2"),
  }),
  "9006-03": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString2_1"),
  }),
  "9006-04": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString2_2"),
  }),
  "9006-05": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString5_1"),
  }),
  "9006-06": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString5_2"),
  }),
  "9006-07": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString6_1"),
  }),
  "9006-08": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString6_2"),
  }),
  "9006-09": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString7_1"),
  }),
  "9006-10": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString7_2"),
  }),
  "9006-11": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString8_1"),
  }),
  "9006-12": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString8_2"),
  }),
  "9006-13": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString11_1"),
  }),
  "9006-14": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString11_2"),
  }),
  "9009-01": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString3"),
  }),
  "9009-02": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString4"),
  }),
  "9009-03": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString9"),
  }),
  "9009-04": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString10"),
  }),
  "9009-05": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString12"),
  }),
  "9009-06": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString13"),
  }),
};
