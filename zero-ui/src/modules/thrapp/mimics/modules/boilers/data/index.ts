import { toFieldsMap } from "../..";
import { BOILER_TANK_DATA } from "./boiler-tanks";

export * from "./boiler-tanks";

export const BOILERS_MIMIC_DATA = toFieldsMap({
  ...BOILER_TANK_DATA,
});
