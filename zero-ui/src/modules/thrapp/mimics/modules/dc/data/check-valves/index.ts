import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const placeholderField = <Type extends SensorComponentType>(type: Type) =>
  getField(type, "dc", "placeholder") as unknown as ModuleField<"custom", "dc">;

const checkValve = (yardTag: string) =>
  toInstance<MimicComponentType.CheckValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: placeholderField(SensorComponentType.Valve),
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Check valve",
        componentType: "Check valve",
        yardTag,
      });
    },
  });

const checkValveTags = ["1076-03", "1077-04", "1075-01", "1077-03", "1075-06", "1076-02"];

export const DC_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(
    checkValveTags.map((tag) => [tag, checkValve(tag)]),
  ),
});
