import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Switch valve",
  itemName: "2 way valve DN 25",
  yardTag,
  technicalName,
});

export const PVT_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1067-01": toInstance<MimicComponentType.SwitchValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtSwitchMainFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {},
      source: getField(SensorComponentType.Valve, "pvt", "pvtSwitchMainFwd"),
      sensors: {},
      tooltip: tooltip("1067-01", "pvt-switch-main-fwd"),
    }),
    "1067-02": toInstance<MimicComponentType.SwitchValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtSwitchMainAft"),
      },
      controllerState: {},
      custom: {},
      parameters: {},
      source: getField(SensorComponentType.Valve, "pvt", "pvtSwitchMainAft"),
      sensors: {},
      tooltip: tooltip("1067-02", "pvt-switch-main-aft"),
    }),
    "1069-01": toInstance<MimicComponentType.SwitchValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtSwitchOwners"),
      },
      controllerState: {},
      custom: {},
      parameters: {},
      source: getField(SensorComponentType.Valve, "pvt", "pvtSwitchOwners"),
      sensors: {},
      tooltip: tooltip("1069-01", "pvt-switch-owners"),
    }),
  },
});
