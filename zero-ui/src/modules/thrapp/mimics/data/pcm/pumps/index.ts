import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toPump } from "../../helpers";

export const PCM_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1017": toPump({
      source: getField(SensorComponentType.Pump, "pcm", "pcmPump"),
      controls: {
        pump: getField(ControlComponentType.Pump, "pcm", "pcmPump"),
      },
    }),
  },
});
