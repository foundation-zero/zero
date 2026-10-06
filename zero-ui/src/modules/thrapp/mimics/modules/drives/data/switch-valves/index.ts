import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Switch valve",
    componentType: "2 way valve DN 25",
  });

type DrivesSwitchValveField =
  | "drivesSwitchPropdriveAft1"
  | "drivesSwitchPropdriveAft2"
  | "drivesSwitchPropdriveFwd1"
  | "drivesSwitchPropdriveFwd2"
  | "drivesSwitchShorepowerSupply"
  | "drivesSwitchShorepowerReturn";

const switchValve = (field: DrivesSwitchValveField) =>
  toInstance<MimicComponentType.SwitchValve>({
    controls: {
      valve: getField(ControlComponentType.Valve, "drives", field),
    },
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getField(SensorComponentType.Valve, "drives", field),
    get tooltip() {
      return tooltip(this.source);
    },
  });

export const DRIVES_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1069-09": switchValve("drivesSwitchPropdriveAft2"),
    "1069-06": switchValve("drivesSwitchPropdriveAft1"),
    "1069-08": switchValve("drivesSwitchPropdriveFwd2"),
    "1069-07": switchValve("drivesSwitchPropdriveFwd1"),
    "1069-04": switchValve("drivesSwitchShorepowerSupply"),
    "1069-05": switchValve("drivesSwitchShorepowerReturn"),
  },
});
