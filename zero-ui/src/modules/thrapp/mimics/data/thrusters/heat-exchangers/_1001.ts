import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toHeatExchanger } from "../../helpers";

import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { getField } from "../../../providers";

export default toHeatExchanger(
  {
    custom: {
      sideA: HeatExchangerPortOrientation.Side,
      sideB: HeatExchangerPortOrientation.Top,
    },
    source: getField(
      SensorComponentType.HeatTransferDevice,
      "thrusters",
      "thrustersSeawaterExchanger",
    ),
  },
  { title: "Heat Exchanger", componentType: "Heat Exchanger" },
);
