import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toFlowControlValve, valveFields } from "../../helpers";

export const PCM_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1064-04": toFlowControlValve(valveFields("pcm", "pcmFlowcontrolModule1"), {
      componentType: "Flow control valve",
    }),
    "1064-05": toFlowControlValve(valveFields("pcm", "pcmFlowcontrolModule2"), {
      componentType: "Flow control valve",
    }),
    "1064-06": toFlowControlValve(valveFields("pcm", "pcmFlowcontrolModule3"), {
      componentType: "Flow control valve",
    }),
    "1064-07": toFlowControlValve(valveFields("pcm", "pcmFlowcontrolModule4"), {
      componentType: "Flow control valve",
    }),
    "1065-01": toFlowControlValve(valveFields("consumers", "consumersFlowcontrolDhw"), {
      componentType: "Flow control valve",
    }),
    "1061": toFlowControlValve(valveFields("consumers", "consumersFlowcontrolAdsorption"), {
      componentType: "Flow control valve",
    }),
    "1062-01": toFlowControlValve(valveFields("consumers", "consumersFlowcontrolBypass"), {
      componentType: "Flow control valve",
    }),
  },
});
