import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

export const PCM_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-18": toFlowSensor({
      source: getField(SensorComponentType.Flow, "pcm", "pcmFlowModule1"),
    }),
    "1057-19": toFlowSensor({
      source: getField(SensorComponentType.Flow, "pcm", "pcmFlowModule2"),
    }),
    "1057-20": toFlowSensor({
      source: getField(SensorComponentType.Flow, "pcm", "pcmFlowModule3"),
    }),
    "1057-21": toFlowSensor({
      source: getField(SensorComponentType.Flow, "pcm", "pcmFlowModule4"),
    }),
    "1058-07": toFlowSensor({
      source: getField(SensorComponentType.Flow, "consumers", "consumersFlowDhw"),
    }),
    "1058-08": toFlowSensor({
      source: getField(SensorComponentType.Flow, "consumers", "consumersFlowAdsorption"),
    }),
    "1192": toFlowSensor({
      source: getField(SensorComponentType.Flow, "consumers", "consumersFlowBypass"),
    }),
  },
});
