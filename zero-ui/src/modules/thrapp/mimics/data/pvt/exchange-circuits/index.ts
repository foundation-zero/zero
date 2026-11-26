import { SensorComponentType } from "@/modules/thrapp/types/thrs";
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
    // The main bimini feeds two circuits: AFT (strings 1-6) and FWD (strings 7-13).
    "main-fwd": toConnectingCircuit(
      {
        custom: {
          circuitName: "PVT FWD",
          modeModule: "pvt",
          modeTargets: ["fwd"],
        },
        source: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPvtMainFwdHeat"),
      },
      { componentType: "PVT FWD loop" },
    ),
    "main-aft": toConnectingCircuit(
      {
        custom: {
          circuitName: "PVT AFT",
          modeModule: "pvt",
          modeTargets: ["aft"],
        },
        source: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPvtMainAftHeat"),
      },
      { componentType: "PVT AFT loop" },
    ),
    owners: toConnectingCircuit(
      {
        custom: {
          circuitName: "PVT",
          modeModule: "pvt",
          modeTargets: ["owners"],
        },
        source: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPvtOwnersHeat"),
      },
      { componentType: "PVT owners loop" },
    ),
  },
});
