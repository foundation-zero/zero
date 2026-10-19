import { CustomFieldDefinitions } from "@/modules/thrapp/types/fields";
import { ControllerStateComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { getField } from "../../../providers";
import { DHW_TANK_DATA } from "../boiler-tanks";

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
