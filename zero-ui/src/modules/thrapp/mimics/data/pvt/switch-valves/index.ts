import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toSwitchValve } from "../../helpers";

export const PVT_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1067-01": toSwitchValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtSwitchMainFwd"),
      },
      source: getField(SensorComponentType.Valve, "pvt", "pvtSwitchMainFwd"),
    }),
    "1067-02": toSwitchValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtSwitchMainAft"),
      },
      source: getField(SensorComponentType.Valve, "pvt", "pvtSwitchMainAft"),
    }),
    "1069-01": toSwitchValve({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtSwitchOwners"),
      },
      source: getField(SensorComponentType.Valve, "pvt", "pvtSwitchOwners"),
    }),
  },
});
