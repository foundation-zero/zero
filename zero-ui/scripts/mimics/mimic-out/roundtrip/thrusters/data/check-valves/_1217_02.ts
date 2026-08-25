import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.CheckValve>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("thrusters", {
      yardTag: "1217-02",
      technicalName: "thrusters-check-valve-1217-02",
    }),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Check valve",
      componentType: "Check valve",
    });
  },
});
