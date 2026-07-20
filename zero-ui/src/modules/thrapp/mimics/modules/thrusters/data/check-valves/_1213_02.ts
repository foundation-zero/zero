import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.CheckValve>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getCustomField("thrusters", "thrusters-check-valve-1213-01"),
  tooltip: tooltip({
    yardTag: "1213-01",
    technicalName: "thrusters-check-valve-1213-01",
  }),
});
