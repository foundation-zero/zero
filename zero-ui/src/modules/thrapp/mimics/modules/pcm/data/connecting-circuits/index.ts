import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { DHW_MIMIC_DATA } from "../../../dhw/data";
import { PVT_MIMIC_DATA } from "../../../pvt/data";
import { THRUSTERS_MIMIC_DATA } from "../../../thrusters/data";

export const PCM_CONNECTING_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ConnectingCircuit]: {
    freshwater: DHW_MIMIC_DATA[MimicComponentType.ConnectingCircuit].freshwater,
    pvt: PVT_MIMIC_DATA[MimicComponentType.ConnectingCircuit].pcm,
    thrusters: THRUSTERS_MIMIC_DATA[MimicComponentType.ConnectingCircuit].pcm,
  },
});
