import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toPump } from "../../helpers";

import { getField } from "../../../providers";
import { pumpFlowController } from "../controllers";

export default toPump(
  {
    custom: {
      flowController: pumpFlowController,
    },
    source: getField(SensorComponentType.Pump, "dhw", "dhwPump"),
    controls: {
      pump: getField(ControlComponentType.Pump, "dhw", "dhwPump"),
    },
    parameters: {
      flow: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
      temperature: getField(ParametersType.Temperature, "dhw", "heatpumpTemperatureSetpoint"),
    },
  },
  { componentType: "Circulation pump boosting" },
);
