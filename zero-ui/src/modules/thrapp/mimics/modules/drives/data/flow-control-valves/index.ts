import { MimicComponentType } from "@/modules/thrapp/types";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DrivesFlowControlValveField =
  | "drivesFlowcontrolPropdriveAft"
  | "drivesFlowcontrolPropdriveFwd";

const flowControlValve = (field: DrivesFlowControlValveField) => {
  const source = getField(SensorComponentType.Valve, "drives", field);
  return toInstance<MimicComponentType.FlowControlValve>({
    controls: {
      valve: getField(ControlComponentType.Valve, "drives", field),
    },
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Flow control valve",
        componentType: "2 way valve DN 25",
      });
    },
  });
};

export const DRIVES_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1065-02": flowControlValve("drivesFlowcontrolPropdriveAft"),
    "1065-03": flowControlValve("drivesFlowcontrolPropdriveFwd"),
  },
});
