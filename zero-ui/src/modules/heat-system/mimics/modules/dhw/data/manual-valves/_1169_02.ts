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
    technicalName: "dhw-manual-valve-1169-02",
    yardTag: "1169-02",
  }),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
