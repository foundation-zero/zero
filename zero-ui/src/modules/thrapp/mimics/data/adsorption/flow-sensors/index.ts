import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

export const ADSORPTION_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1058-02": toFlowSensor({
      source: getField(SensorComponentType.Flow, "adsorption", "adsorptionFlowHot"),
    }),
    "1058-09": toFlowSensor({
      source: getField(SensorComponentType.Flow, "adsorption", "adsorptionFlowHt"),
    }),
    "1058-10": toFlowSensor({
      source: getField(SensorComponentType.Flow, "adsorption", "adsorptionFlowDhw"),
    }),
    "1059": toFlowSensor({
      source: getField(SensorComponentType.Flow, "adsorption", "adsorptionFlowWaste"),
    }),
  },
});
