import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _1064_03 from "./_1064_03";
import _1064_08 from "./_1064_08";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Flow Control valve",
  itemName: "2 way valve DN 25",
  ...content,
});

export const setpointName = "boilers_filling_temperature";

export const toFlowControlValve = toInstance<MimicComponentType.FlowControlValve>;

export const BOILER_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1064-08": _1064_08,
    "1064-03": _1064_03,
  },
});
