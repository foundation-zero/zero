import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type DrivesTemperatureField =
  | "drivesTemperaturePropdriveAft2Return"
  | "drivesTemperaturePropdriveAft1Return"
  | "drivesTemperaturePropdriveFwd2Return"
  | "drivesTemperaturePropdriveFwd1Return"
  | "drivesTemperaturePropdrivesAftSupply"
  | "drivesTemperaturePropdrivesFwdSupply"
  | "drivesTemperatureShorepowerReturn"
  | "drivesTemperatureRecovery"
  | "drivesTemperatureSupply"
  | "drivesTemperatureRecoveryReturn"
  | "drivesTemperatureRecoveryMix";

export const tooltip = (
  field: ModuleField<SensorComponentType.Temperature, "drives">,
): TooltipContent =>
  fieldTooltip(field, {
    title: "Temperature sensor",
    componentType: "Temperature sensor",
  });

const temperatureSensor = (field: DrivesTemperatureField) => {
  const source = getField(SensorComponentType.Temperature, "drives", field);
  return toInstance<MimicComponentType.TemperatureSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: { measurement: source },
    source,
    get tooltip() {
      return tooltip(this.source);
    },
  });
};

export const DRIVES_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-64": temperatureSensor("drivesTemperaturePropdriveAft2Return"),
    "1038-32": temperatureSensor("drivesTemperaturePropdriveAft1Return"),
    "1038-72": temperatureSensor("drivesTemperaturePropdriveFwd2Return"),
    "1038-61": temperatureSensor("drivesTemperaturePropdriveFwd1Return"),
    "1038-63": temperatureSensor("drivesTemperaturePropdrivesAftSupply"),
    "1038-62": temperatureSensor("drivesTemperaturePropdrivesFwdSupply"),
    "1038-11": temperatureSensor("drivesTemperatureShorepowerReturn"),
    "1038-16": temperatureSensor("drivesTemperatureRecovery"),
    "1038-14": temperatureSensor("drivesTemperatureSupply"),
    "1038-59": temperatureSensor("drivesTemperatureRecoveryReturn"),
    "1038-57": temperatureSensor("drivesTemperatureRecoveryMix"),
  },
});
