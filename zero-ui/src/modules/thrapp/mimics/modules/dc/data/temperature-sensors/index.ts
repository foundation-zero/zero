import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DcTemperatureField =
  | "dcTemperatureAftSupply"
  | "dcTemperatureRecoveryMix"
  | "dcTemperatureSupply"
  | "dcTemperatureFwdReturn"
  | "dcTemperatureAftReturn"
  | "dcTemperatureRecovery"
  | "dcTemperatureRecoveryReturn"
  | "dcTemperatureFwdSupply"
  | "dcTemperatureUgridSupply"
  | "dcTemperatureUgridReturn";

const temperatureTooltip = (
  field: ModuleField<SensorComponentType.Temperature, "dc">,
): TooltipContent =>
  fieldTooltip(field, {
    title: "Temperature sensor",
    componentType: "Temperature sensor",
  });

const temperatureSensor = (field: DcTemperatureField) => {
  const source = getField(SensorComponentType.Temperature, "dc", field);
  return toInstance<MimicComponentType.TemperatureSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: { measurement: source },
    source,
    get tooltip() {
      return temperatureTooltip(this.source);
    },
  });
};

export const DC_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-15": temperatureSensor("dcTemperatureAftSupply"),
    "1038-17": temperatureSensor("dcTemperatureRecoveryMix"),
    "1038-18": temperatureSensor("dcTemperatureSupply"),
    "1038-19": temperatureSensor("dcTemperatureFwdReturn"),
    "1038-20": temperatureSensor("dcTemperatureAftReturn"),
    "1038-52": temperatureSensor("dcTemperatureRecovery"),
    "1038-58": temperatureSensor("dcTemperatureRecoveryReturn"),
    "1038-69": temperatureSensor("dcTemperatureFwdSupply"),
    "1038-70": temperatureSensor("dcTemperatureUgridSupply"),
    "1038-71": temperatureSensor("dcTemperatureUgridReturn"),
  },
});
