import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: undefined,
  tooltip: tooltip("1084-01", "thrusters-manual-valve-1084-01"),
});
