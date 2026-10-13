import { SensorComponentType } from "@/modules/heat-system-simulation/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.SeawaterCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Seawater",
  },
  parameters: {},
  source: getField(SensorComponentType.Temperature, "thrusters", "placeholder"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Seawater circuit",
      componentType: "Seawater",
    });
  },
});
