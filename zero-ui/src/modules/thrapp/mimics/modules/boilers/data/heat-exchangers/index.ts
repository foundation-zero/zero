import { SensorComponentType } from "@/modules/thrs/types";

import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import _1004 from "./_1004";
import _1007 from "./_1007";
import _1008 from "./_1008";
import _1009 from "./_1009";

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

export const toHeatExchanger = toInstance<MimicComponentType.HeatExchanger>;

export const BOILER_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1007": _1007,
    "1009": _1009,
    "1008": _1008,
    "1004": _1004,
  },
});
