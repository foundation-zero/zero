import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { CustomFieldDefinitions } from "@/modules/thrapp/types/fields";
import { ControllerStateComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { DHW_TANK_DATA } from "../boiler-tanks";
import { fieldTooltip } from "../shared";

export const tooltip = (field: ModuleField<SensorComponentType>): TooltipContent =>
  fieldTooltip(field, {
    title: "Switch valve",
    componentType: "2 way valve DN 25",
  });

export const controller = getField(
  ControllerStateComponentType.DhwTanksController,
  "dhw",
  "dhwTanksController",
);

type SwitchValveCustom = CustomFieldDefinitions[MimicComponentType.SwitchValve];

export const tank1: SwitchValveCustom = {
  get tankController() {
    return DHW_TANK_DATA[MimicComponentType.BoilerTank]["1053"];
  },
};

export const tank2: SwitchValveCustom = {
  get tankController() {
    return DHW_TANK_DATA[MimicComponentType.BoilerTank]["1054"];
  },
};

export const tank3: SwitchValveCustom = {
  get tankController() {
    return DHW_TANK_DATA[MimicComponentType.BoilerTank]["1055"];
  },
};
