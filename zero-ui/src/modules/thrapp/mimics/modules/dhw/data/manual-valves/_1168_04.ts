import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", {
    technicalName: "dhw-manual-valve-1168-04",
    yardTag: "1168-04",
  }),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
