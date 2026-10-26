import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toSwitchValve, valveFields } from "../../helpers";

export const PCM_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1190-01": toSwitchValve(valveFields("pcm", "pcmSwitchChargingSupply"), {
      componentType: "Switch valve",
    }),
    "1066-01": toSwitchValve(valveFields("pcm", "pcmSwitchDischarging"), {
      componentType: "Switch valve",
    }),
    "1062-02": toSwitchValve(valveFields("pcm", "pcmSwitchChargingReturn"), {
      componentType: "Switch valve",
    }),
    "1066-02": toSwitchValve(valveFields("consumers", "consumersSwitchAdsorption"), {
      componentType: "Switch valve",
    }),
    "1067-15": toSwitchValve(valveFields("consumers", "consumersSwitchDhw"), {
      componentType: "Switch valve",
    }),
    "1071-02": toSwitchValve(valveFields("pcm", "pcmSwitchConsumers"), {
      componentType: "Switch valve",
    }),
  },
});
