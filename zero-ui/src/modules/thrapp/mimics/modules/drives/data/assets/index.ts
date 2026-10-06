import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";

export const DRIVES_ASSET_DATA = toFieldsMap({
  [MimicComponentType.DcConverter]: {
    shorepower: toInstance<MimicComponentType.DcConverter>({
      controls: {},
      controllerState: {},
      custom: {
        converters: [
          getField(SensorComponentType.ShorePowerConverter, "drives", "drivesShorepower"),
        ],
        group: "shorepower",
      },
      parameters: {},
      sensors: {
        heatTransfer: getField(SensorComponentType.HeatTransferDevice, "drives", "placeholder"),
        power: getField(SensorComponentType.Pvt, "drives", "placeholder"),
        temperature: getField(SensorComponentType.Temperature, "drives", "placeholder"),
      },
      source: undefined,
      tooltip: {
        title: "shorepower",
      },
    }),
  },
});
