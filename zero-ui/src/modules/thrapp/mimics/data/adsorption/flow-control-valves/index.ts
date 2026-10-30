import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toFlowControlValve, valveFields } from "../../helpers";

export const ADSORPTION_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1062-03": toFlowControlValve(valveFields("adsorption", "adsorptionFlowcontrolWaste")),
  },
});
