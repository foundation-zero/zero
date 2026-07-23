import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { PVT_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  controllerState: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Top,
    sideB: HeatExchangerPortOrientation.Side,
    exchangeCircuit: PVT_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].seawater,
  },
  source: getField(SensorComponentType.HeatExchanger, "pvt", "pvtMixExchanger"),
  parameters: {},
  sensors: {
    incoming: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
    outgoing: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
    flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
  },
  // tooltip: tooltip({
  //   yardTag: "1002",
  //   technicalName: "pvt-heat-exchanger-main",
  // }),
  get tooltip() {
    return tooltip(this.source);
  },
});
