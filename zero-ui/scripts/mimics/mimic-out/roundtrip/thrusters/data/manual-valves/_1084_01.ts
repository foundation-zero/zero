import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.ManualValve>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("thrusters", {
      yardTag: "1084-01",
      technicalName: "thrusters-manual-valve-1084-01",
    }),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Manual valve",
      componentType: "Manual valve",
    });
  },
});
