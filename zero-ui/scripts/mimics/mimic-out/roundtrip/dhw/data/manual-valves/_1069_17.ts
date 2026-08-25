import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.ManualValve>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("dhw", {
      yardTag: "1069-17",
      technicalName: "dhw-manual-valve-1069-17",
    }),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Manual valve",
      componentType: "Manual valve",
    });
  },
});
