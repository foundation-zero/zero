import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { CustomFieldDefinitions } from "@/modules/thrapp/types/fields";
import { ControllerStateComponentType } from "@/modules/thrs/types";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { DHW_TANK_DATA } from "../boiler-tanks";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Switch valve",
  itemName: "2 way valve DN 25",
  ...content,
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
