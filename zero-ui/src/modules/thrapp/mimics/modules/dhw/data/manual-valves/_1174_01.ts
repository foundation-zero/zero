import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ManualValve>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getCustomField("dhw", {
    technicalName: "dhw-manual-valve-1174-01",
    yardTag: "1174-01",
  }),
  get tooltip() {
    return tooltip(this.source);
  },
});
