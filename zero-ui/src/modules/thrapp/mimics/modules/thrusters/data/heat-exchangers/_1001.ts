import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  controllerState: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
  },
  source: getField(
    SensorComponentType.HeatTransferDevice,
    "thrusters",
    "thrustersSeawaterExchanger",
  ),
  parameters: {},
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
