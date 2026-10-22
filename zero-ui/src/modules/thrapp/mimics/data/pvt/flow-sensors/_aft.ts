import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

// Flow sensors of the PVT AFT strings.
// 9006-02 (string 1.2) has no thrsim field yet.
export const PVT_AFT_FLOW_SENSORS = {
  "9006-01": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString11"),
  }),
  "9006-02": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "placeholder"),
  }),
  "9006-03": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString21"),
  }),
  "9006-04": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString22"),
  }),
  "9006-05": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString51"),
  }),
  "9006-06": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString52"),
  }),
  "9006-07": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString61"),
  }),
  "9006-08": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString62"),
  }),
  "9006-09": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString71"),
  }),
  "9006-10": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString72"),
  }),
  "9006-11": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString81"),
  }),
  "9006-12": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString82"),
  }),
  "9006-13": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString111"),
  }),
  "9006-14": toFlowSensor({
    source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString112"),
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
