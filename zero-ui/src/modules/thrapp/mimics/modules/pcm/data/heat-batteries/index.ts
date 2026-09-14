import { getField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

const createHeatBattery = (
  title: string,
  yardTag: string,
  source: ModuleField<SensorComponentType.Pcm>,
) =>
  toInstance<MimicComponentType.Pcm>({
    source,
    sensors: {},
    controls: {},
    controllerState: {},
    parameters: {},
    custom: {},
    tooltip: {
      title,
      yardTag,
      componentType: "PCM",
    },
  });

export const PCM_HEAT_BATTERIES_DATA = toFieldsMap({
  [MimicComponentType.Pcm]: {
    "1049": createHeatBattery(
      "Heat battery 1",
      "1049",
      getField(SensorComponentType.Pcm, "pcm", "pcmModule1"),
    ),
    "1050": createHeatBattery(
      "Heat battery 2",
      "1050",
      getField(SensorComponentType.Pcm, "pcm", "pcmModule2"),
    ),
    "1051": createHeatBattery(
      "Heat battery 3",
      "1051",
      getField(SensorComponentType.Pcm, "pcm", "pcmModule3"),
    ),
    "1052": createHeatBattery(
      "Heat battery 4",
      "1052",
      getField(SensorComponentType.Pcm, "pcm", "pcmModule4"),
    ),
  },
});
