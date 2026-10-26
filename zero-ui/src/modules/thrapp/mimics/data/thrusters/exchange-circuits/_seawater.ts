import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toSeawaterCircuit } from "../../helpers";

export default toSeawaterCircuit(
  {
    custom: {
      circuitName: "Seawater",
    },
    source: getField(SensorComponentType.Temperature, "thrusters", "placeholder"),
  },
  { componentType: "Seawater" },
);
