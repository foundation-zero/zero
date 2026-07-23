import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Switch valve",
    componentType: "2 way valve DN 25",
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
      get tooltip() {
        return tooltip(this.source);
      },
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
      get tooltip() {
        return tooltip(this.source);
      },
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
      get tooltip() {
        return tooltip(this.source);
      },
    }),
  },
});
