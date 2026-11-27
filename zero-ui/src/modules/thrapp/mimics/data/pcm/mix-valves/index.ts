import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toMixValve } from "../../helpers";

export const PCM_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    // The fresh water system drives this valve, THRS cannot.
    "25001135": toMixValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pcm", "placeholder"),
      },
      source: getField(SensorComponentType.Valve, "freshWaterHot", "hotMixPcm"),
    }),
  },
});
