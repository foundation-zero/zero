import { SensorComponentType } from "@/modules/thrs/types";

import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { toFieldsMap } from "../..";
import { MimicComponentType } from "../../../../types";
import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { getField } from "../../../providers";

const tooltip = (tooltip: Partial<TooltipContent>): TooltipContent => ({
  title: "Heat Exchanger",
  itemName: "Heat Exchanger",
  ...tooltip,
});

export const BOILER_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1007": {
      controls: {},
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Side,
        circuit: {
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
        },
        exchangeCircuit: {
          incoming: getField(
            SensorComponentType.Temperature,
            "pvt",
            "pvtTemperatureMainString11Return",
          ),
          outgoing: getField(
            SensorComponentType.Temperature,
            "boilers",
            "fahrenheitTemperatureBoilersReturn",
          ),
          flow: getField(SensorComponentType.Flow, "boilers", "fahrenheitFlowBoilers"),
          deltaT: getField(SensorComponentType.DeltaT, "boilers", "fahrenheitDelta"),
        },
      },
      parameters: {},
      sensors: {
        heatExchanger: getField(
          SensorComponentType.HeatExchanger,
          "boilers",
          "boilersFahrenheitExchanger",
        ),
      },
      tooltip: tooltip({
        yardTag: "1007",
        technicalName: "Fahrenheit-HotWater-Exchanger",
      }),
    },
    "1009": {
      controls: {},
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Top,
        circuit: {
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
        },
        exchangeCircuit: {
          incoming: getField(
            SensorComponentType.Temperature,
            "pvt",
            "pvtTemperatureMainString11Return",
          ),
          outgoing: getField(
            SensorComponentType.Temperature,
            "boilers",
            "fahrenheitTemperatureBoilersReturn",
          ),
          flow: getField(SensorComponentType.Flow, "boilers", "fahrenheitFlowBoilers"),
          deltaT: getField(SensorComponentType.DeltaT, "boilers", "fahrenheitDelta"),
        },
      },
      parameters: {},
      sensors: {
        heatExchanger: getField(
          SensorComponentType.HeatExchanger,
          "boilers",
          "boilersLt1Exchanger",
        ),
      },
      tooltip: tooltip({
        yardTag: "1009",
        technicalName: "boilersLt1Exchanger",
      }),
    },
    "1008": {
      controls: {},
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Top,
        circuit: {
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
        },
        exchangeCircuit: {
          incoming: getField(
            SensorComponentType.Temperature,
            "pvt",
            "pvtTemperatureMainString11Return",
          ),
          outgoing: getField(
            SensorComponentType.Temperature,
            "boilers",
            "fahrenheitTemperatureBoilersReturn",
          ),
          flow: getField(SensorComponentType.Flow, "boilers", "fahrenheitFlowBoilers"),
          deltaT: getField(SensorComponentType.DeltaT, "boilers", "fahrenheitDelta"),
        },
      },
      parameters: {},
      sensors: {
        heatExchanger: getField(
          SensorComponentType.HeatExchanger,
          "boilers",
          "boilersLt2Exchanger",
        ),
      },
      tooltip: tooltip({
        yardTag: "1008",
        technicalName: "boilersLt2Exchanger",
      }),
    },
    "1004": {
      controls: {},
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Top,
        circuit: {
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
        },
        exchangeCircuit: {
          incoming: getField(
            SensorComponentType.Temperature,
            "pvt",
            "pvtTemperatureMainString11Return",
          ),
          outgoing: getField(
            SensorComponentType.Temperature,
            "boilers",
            "fahrenheitTemperatureBoilersReturn",
          ),
          flow: getField(SensorComponentType.Flow, "boilers", "fahrenheitFlowBoilers"),
          deltaT: getField(SensorComponentType.DeltaT, "boilers", "fahrenheitDelta"),
        },
      },
      parameters: {},
      sensors: {
        heatExchanger: getField(
          SensorComponentType.HeatExchanger,
          "boilers",
          "boilersFahrenheitExchanger",
        ),
      },
      tooltip: tooltip({
        yardTag: "1004",
        technicalName: "Fahrenheit-HotWater-Exchanger",
      }),
    },
  },
});
