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
    // Both main bimini sections (AFT strings 1-6, FWD strings 7-13) feed this circuit.
    main: toConnectingCircuit(
      {
        custom: {
          circuitName: "PVT",
          modeModule: "pvt",
        },
        source: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPvtMainHeat"),
      },
      { componentType: "PVT main loop" },
    ),
  },
});
