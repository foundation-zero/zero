import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toMixValve } from "../../helpers";
import {
  pvtHeatDumpController,
  pvtMainAftWarmupMixController,
  pvtMainFwdWarmupMixController,
  pvtOwnersWarmupMixController,
} from "../controllers";

export const PVT_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1044-01": toMixValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixMainFwd"),
      },
      custom: { controller: pvtMainFwdWarmupMixController },
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixMainFwd"),
    }),
    "1044-02": toMixValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixMainAft"),
      },
      custom: { controller: pvtMainAftWarmupMixController },
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixMainAft"),
    }),
    "1043-01": toMixValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixOwners"),
      },
      custom: { controller: pvtOwnersWarmupMixController },
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixOwners"),
    }),
    "1047-02": toMixValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixExchanger"),
      },
      custom: { controller: pvtHeatDumpController },
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixExchanger"),
    }),
  },
});
