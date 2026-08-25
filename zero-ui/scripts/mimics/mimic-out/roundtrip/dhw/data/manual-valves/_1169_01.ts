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
      yardTag: "1169-01",
      technicalName: "dhw-manual-valve-1169-01",
    }),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Manual valve",
      componentType: "Manual valve",
    });
  },
});
