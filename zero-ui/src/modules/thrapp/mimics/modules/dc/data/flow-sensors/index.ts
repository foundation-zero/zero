import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DcFlowField = "dcFlowAftReturn" | "dcFlowUgridReturn" | "dcFlowFwdReturn" | "dcFlowRecovery";

const flowTooltip = (field: ModuleField<SensorComponentType.Flow, "dc">): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow sensor",
    componentType: "Flow sensor",
  });

const flowSensor = (field: DcFlowField) => {
  const source = getField(SensorComponentType.Flow, "dc", field);
  return toInstance<MimicComponentType.FlowSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return flowTooltip(this.source);
    },
  });
};

export const DC_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-25": flowSensor("dcFlowAftReturn"),
    "1057-26": flowSensor("dcFlowFwdReturn"),
    "1058-06": flowSensor("dcFlowUgridReturn"),
    "1058-04": flowSensor("dcFlowRecovery"),
  },
});
