import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toConnectingCircuit, toSeawaterCircuit } from "../../helpers";

export const PVT_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.SeawaterCircuit]: {
    seawater: toSeawaterCircuit({
      custom: {
        circuitName: "Seawater",
      },
      source: getField(SensorComponentType.Temperature, "pvt", "placeholder"),
    }),
  },
  [MimicComponentType.ConnectingCircuit]: {
    pcm: toConnectingCircuit(
      {
        custom: {
          circuitName: "PCM",
          modeModule: "pcm",
        },
        source: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPcmHeat"),
      },
      { componentType: "PCM loop" },
    ),
  },
});
