import { MimicComponentType } from "@/modules/thrapp/types";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DcMixValveField = "dcMixAft" | "dcMixFwd" | "dcMixUgrid" | "dcMixRecovery" | "dcMixExchanger";

const mixValve = (field: DcMixValveField) => {
  const source = getField(SensorComponentType.Valve, "dc", field);
  return toInstance<MimicComponentType.MixValve>({
    controls: {
      valve: getField(ControlComponentType.Valve, "dc", field),
    },
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Mix valve",
        componentType: "3 way valve DN 25",
      });
    },
  });
};

export const DC_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1043-02": mixValve("dcMixAft"),
    "1042-03": mixValve("dcMixFwd"),
    "1045-01": mixValve("dcMixUgrid"),
    "1046-04": mixValve("dcMixRecovery"),
    "1046-05": mixValve("dcMixExchanger"),
  },
});
