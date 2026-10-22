import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toFlowControlValve, valveFields } from "../../helpers";

export const DRIVES_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1065-02": toFlowControlValve(valveFields("drives", "drivesFlowcontrolPropdriveAft")),
    "1065-03": toFlowControlValve(valveFields("drives", "drivesFlowcontrolPropdriveFwd")),
  },
});
