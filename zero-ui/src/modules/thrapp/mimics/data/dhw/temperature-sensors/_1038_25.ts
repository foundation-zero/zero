import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toTemperatureSensor } from "../../helpers";

import { getField } from "../../../providers";
import { dcFlowController } from "../controllers";

export default toTemperatureSensor(
  {
    custom: {
      controller: dcFlowController,
    },
    source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
  },
  { componentType: "Temperature sensor Pt100 RTD" },
);
