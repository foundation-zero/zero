import { getField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

const createHeatBattery = (title: string, source: ModuleField<SensorComponentType.Pcm>) =>
  toInstance<MimicComponentType.Pcm>({
    source,
    sensors: {},
    controls: {},
    controllerState: {},
    parameters: {},
    custom: {},
    get tooltip() {
      return fieldTooltip(this.source, {
        title: title,
        componentType: "PCM",
      });
    },
  });

export const PCM_HEAT_BATTERIES_DATA = toFieldsMap({
  [MimicComponentType.Pcm]: {
    "1049": createHeatBattery(
      "Heat battery 1",
      getField(SensorComponentType.Pcm, "pcm", "pcmHeatModule1"),
    ),
    "1050": createHeatBattery(
      "Heat battery 2",
      getField(SensorComponentType.Pcm, "pcm", "pcmHeatModule2"),
    ),
    "1051": createHeatBattery(
      "Heat battery 3",
      getField(SensorComponentType.Pcm, "pcm", "pcmHeatModule3"),
    ),
    "1052": createHeatBattery(
      "Heat battery 4",
      getField(SensorComponentType.Pcm, "pcm", "pcmHeatModule4"),
    ),
  },
});
