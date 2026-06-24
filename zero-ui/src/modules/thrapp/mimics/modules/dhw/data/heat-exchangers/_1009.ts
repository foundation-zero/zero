import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { DHW_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
    get exchangeCircuit() {
      return DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].drives.sensors;
    },
  },
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDrivesExchanger"),
  sensors: {
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDrivesReturn"),
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives"),
  },
  tooltip: tooltip({
    yardTag: "1009",
    technicalName: "dhwDrivesExchanger",
  }),
});
