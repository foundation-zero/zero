import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DrivesFlowField =
  | "drivesFlowPropdriveAft2"
  | "drivesFlowPropdriveAft1"
  | "drivesFlowPropdriveFwd2"
  | "drivesFlowPropdriveFwd1"
  | "drivesFlowShorepower"
  | "drivesFlowRecovery";

export const tooltip = (field: ModuleField<SensorComponentType.Flow, "drives">): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow sensor",
    componentType: "Flow sensor",
  });

const flowSensor = (field: DrivesFlowField) => {
  const source = getField(SensorComponentType.Flow, "drives", field);
  return toInstance<MimicComponentType.FlowSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return tooltip(this.source);
    },
  });
};

export const DRIVES_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-16": flowSensor("drivesFlowPropdriveAft2"),
    "1057-13": flowSensor("drivesFlowPropdriveAft1"),
    "1057-14": flowSensor("drivesFlowPropdriveFwd2"),
    "1057-15": flowSensor("drivesFlowPropdriveFwd1"),
    "1057-10": flowSensor("drivesFlowShorepower"),
    "1058-03": flowSensor("drivesFlowRecovery"),
  },
});
