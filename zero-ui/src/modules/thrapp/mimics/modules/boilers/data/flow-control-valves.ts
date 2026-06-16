import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { toFieldsMap } from "../..";
import { MimicComponentType } from "../../../../types";
import { getField } from "../../../providers";

const tooltip = (tooltip: Partial<TooltipContent>): TooltipContent => ({
  title: "Flow Control valve",
  itemName: "2 way valve DN 25",
  ...tooltip,
});

export const BOILER_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1064-08": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersFlowcontrolLt1"),
        controller: getField(
          ControlComponentType.PIDController,
          "boilers",
          "boilersLt1FlowController",
        ),
      },
      custom: {
        controllerName: "LT1_flow_controller",
        setpointName: "boilers_filling_temperature",
      },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersFlowcontrolLt1"),
        measurement: getField(
          SensorComponentType.Temperature,
          "boilers",
          "boilersTemperatureLt1Return",
        ),
      },
      tooltip: tooltip({
        yardTag: "1064-08",
        technicalName: "boilers-flowcontrol-lt1",
      }),
    },
    "1064-03": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersFlowcontrolLt2"),
        controller: getField(
          ControlComponentType.PIDController,
          "boilers",
          "boilersLt2FlowController",
        ),
      },
      custom: {
        controllerName: "LT2_flow_controller",
        setpointName: "boilers_filling_temperature",
      },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersFlowcontrolLt2"),
        measurement: getField(
          SensorComponentType.Temperature,
          "boilers",
          "boilersTemperatureLt2Return",
        ),
      },
      tooltip: tooltip({
        yardTag: "1064-03",
        technicalName: "boilers-flowcontrol-lt2",
      }),
    },
  },
});
