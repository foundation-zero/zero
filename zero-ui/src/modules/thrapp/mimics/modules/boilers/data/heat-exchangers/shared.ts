import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { SensorComponentType } from "@/modules/thrs/types";

import { getField } from "../../../../providers";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Heat Exchanger",
  itemName: "Heat Exchanger",
  ...content,
});

export const circuit = {
  incoming: getField(
    SensorComponentType.Temperature,
    "boilers",
    "boilersTemperatureFreshwaterSupply",
  ),
  outgoing: getField(
    SensorComponentType.Temperature,
    "boilers",
    "boilersTemperatureFahrenheitReturn",
  ),
  flow: getField(SensorComponentType.Flow, "boilers", "boilersFlowLt2"),
  deltaT: getField(SensorComponentType.DeltaT, "boilers", "fahrenheitDelta"),
};

export const exchangeCircuit = {
  incoming: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString11Return"),
  outgoing: getField(
    SensorComponentType.Temperature,
    "boilers",
    "fahrenheitTemperatureBoilersReturn",
  ),
  flow: getField(SensorComponentType.Flow, "boilers", "fahrenheitFlowBoilers"),
  deltaT: getField(SensorComponentType.DeltaT, "boilers", "fahrenheitDelta"),
};
