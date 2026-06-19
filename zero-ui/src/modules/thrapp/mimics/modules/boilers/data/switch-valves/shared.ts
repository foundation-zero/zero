import { ControlComponentType } from "@/modules/thrs/types";

import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { CustomFieldDefinitions } from "@/modules/thrapp/types/fields";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { BOILER_TANK_DATA } from "../boiler-tanks";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Switch valve",
  itemName: "2 way valve DN 25",
  ...content,
});

export const controller = getField(
  ControlComponentType.BoilersTanksController,
  "boilers",
  "boilersTanksController",
);

type SwitchValveCustom = CustomFieldDefinitions[MimicComponentType.SwitchValve]["tank"];

export const tank1: SwitchValveCustom = {
  controller,
  get operator() {
    return BOILER_TANK_DATA[MimicComponentType.BoilerTank]["1053"].sensors;
  },
  operatorName: "Tank 1 operator",
};

export const tank2: SwitchValveCustom = {
  controller,
  get operator() {
    return BOILER_TANK_DATA[MimicComponentType.BoilerTank]["1054"].sensors;
  },
  operatorName: "Tank 2 operator",
};

export const tank3: SwitchValveCustom = {
  controller,
  get operator() {
    return BOILER_TANK_DATA[MimicComponentType.BoilerTank]["1055"].sensors;
  },
  operatorName: "Tank 3 operator",
};
