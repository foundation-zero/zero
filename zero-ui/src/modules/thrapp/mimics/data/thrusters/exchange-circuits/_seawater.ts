import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toSeawaterCircuit } from "../../helpers";

export default toSeawaterCircuit(
  {
    custom: {
      circuitName: "Seawater",
    },
    source: getField(SensorComponentType.Temperature, "thrusters", "placeholder"),
    sensors: {
      heatTransfer: getField(
        SensorComponentType.HeatTransferDevice,
        "thrusters",
        "thrustersSeawaterExchanger",
      ),
    },
  },
  { componentType: "Seawater" },
);
