import { ThrsDefinitions } from "@/modules/thrsim/lib/consts";
import {
  ControlComponentType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { TooltipComponentContext, TooltipContent } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { toInstance } from "../modules";
import { fieldTooltip } from "../modules/shared";
import { getField, ModuleField } from "../providers";

type TooltipOverrides = Partial<TooltipContent>;

type InstanceFields<Type extends MimicComponentType> = Omit<
  TooltipComponentContext<Type>,
  "tooltip" | "registerField" | "type"
>;

// Fields that accept an empty object, so they can be left out and default to `{}`.
type DefaultedKeys<Fields> = {
  [Key in keyof Fields]-?: object extends Fields[Key] ? Key : never;
}[keyof Fields];

export type InstanceInput<Type extends MimicComponentType> = Omit<
  InstanceFields<Type>,
  DefaultedKeys<InstanceFields<Type>>
> &
  Partial<Pick<InstanceFields<Type>, DefaultedKeys<InstanceFields<Type>>>>;

const defaultFields = {
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
};

/**
 * Creates a builder for components backed by a source field. The tooltip is derived from the
 * source, using `defaults` for the title and component type unless overridden per instance.
 */
const toSourceComponent =
  <Type extends MimicComponentType>(defaults: TooltipOverrides) =>
  (fields: InstanceInput<Type>, tooltip?: TooltipOverrides) =>
    toInstance<Type>({
      ...defaultFields,
      ...fields,
      get tooltip() {
        return fieldTooltip(this.source as ModuleField<SensorComponentType | "custom">, {
          ...defaults,
          ...tooltip,
        });
      },
    } as TooltipComponentContext<Type>);

export const toPressureSensor = toSourceComponent<MimicComponentType.PressureSensor>({
  title: "Pressure sensor",
  componentType: "Pressure sensor",
});

export const toTemperatureSensor = toSourceComponent<MimicComponentType.TemperatureSensor>({
  title: "Temperature sensor",
  componentType: "Temperature sensor",
});

export const toFlowSensor = toSourceComponent<MimicComponentType.FlowSensor>({
  title: "Flow sensor",
  componentType: "Flow sensor",
});

export const toPump = toSourceComponent<MimicComponentType.Pump>({
  title: "Pump",
  componentType: "Circulation pump",
});

export const toSwitchValve = toSourceComponent<MimicComponentType.SwitchValve>({
  title: "Switch valve",
  componentType: "2 way valve DN 25",
});

export const toMixValve = toSourceComponent<MimicComponentType.MixValve>({
  title: "Mix valve",
  componentType: "3 way valve DN 25",
});

export const toFlowControlValve = toSourceComponent<MimicComponentType.FlowControlValve>({
  title: "Flow control valve",
  componentType: "2 way valve DN 25",
});

export const toHeatExchanger = toSourceComponent<MimicComponentType.HeatExchanger>({
  title: "Heat exchanger",
  componentType: "Heat exchanger",
});

export const toExchangeCircuit = toSourceComponent<MimicComponentType.ExchangeCircuit>({
  title: "Exchange circuit",
  componentType: "Exchange circuit",
});

export const toSeawaterCircuit = toSourceComponent<MimicComponentType.SeawaterCircuit>({
  title: "Seawater circuit",
  componentType: "Seawater loop",
});

export const toConnectingCircuit = toSourceComponent<MimicComponentType.ConnectingCircuit>({
  title: "Connecting circuit",
  componentType: "Connecting circuit",
});

// Manual components have no live data, so all their fields are empty.
const emptyFields = {
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: undefined,
};

export const toAirTrapVessel = (yardTag: string, tooltip?: TooltipOverrides) =>
  toInstance<MimicComponentType.AirTrapVessel>({
    ...emptyFields,
    tooltip: { yardTag, title: "Air trap vessel", componentType: "Air trap vessel", ...tooltip },
  });

export const toCheckValve = (yardTag: string, tooltip?: TooltipOverrides) =>
  toInstance<MimicComponentType.CheckValve>({
    ...emptyFields,
    tooltip: { yardTag, title: "Check valve", componentType: "Check valve", ...tooltip },
  });

export const toExpansionTank = (yardTag: string, tooltip?: TooltipOverrides) =>
  toInstance<MimicComponentType.ExpansionTank>({
    ...emptyFields,
    tooltip: { yardTag, title: "Expansion tank", componentType: "Expansion tank", ...tooltip },
  });

export const toExpansionValve = (yardTag: string, tooltip?: TooltipOverrides) =>
  toInstance<MimicComponentType.ExpansionValve>({
    ...emptyFields,
    tooltip: { yardTag, title: "Pressure valve", componentType: "Pressure valve", ...tooltip },
  });

export const toManualPump = (yardTag: string, tooltip?: TooltipOverrides) =>
  toInstance<MimicComponentType.ManualPump>({
    ...emptyFields,
    tooltip: { yardTag, title: "Pump", componentType: "Circulation pump", ...tooltip },
  });

export const toManualValve = (yardTag: string, tooltip?: TooltipOverrides) =>
  toInstance<MimicComponentType.ManualValve>({
    ...emptyFields,
    tooltip: { yardTag, title: "Manual valve", componentType: "2 way valve DN 15", ...tooltip },
  });

export const toPressureGauge = (yardTag: string, tooltip?: TooltipOverrides) =>
  toInstance<MimicComponentType.PressureGauge>({
    ...emptyFields,
    tooltip: {
      yardTag,
      title: "Manual pressure sensor",
      componentType: "Manual pressure sensor",
      ...tooltip,
    },
  });

type Module = keyof ThrsDefinitions;

// A field that a module exposes both as a sensor of type `Sensor` and a control of type `Control`.
type ControlledField<
  M extends Module,
  Sensor extends SensorComponentType,
  Control extends ControlComponentType,
> = PickKeys<ThrsDefinitions[M]["sensorValues"], SchemaDefinition<Sensor>> &
  PickKeys<ThrsDefinitions[M]["controlValues"], SchemaDefinition<Control>>;

/** Source and control fields for a valve that is read and controlled through the same field. */
export const valveFields = <M extends Module>(
  module: M,
  field: ControlledField<M, SensorComponentType.Valve, ControlComponentType.Valve>,
) => ({
  controls: { valve: getField(ControlComponentType.Valve, module, field) },
  source: getField(SensorComponentType.Valve, module, field),
});

/** Source and control fields for a pump that is read and controlled through the same field. */
export const pumpFields = <M extends Module>(
  module: M,
  field: ControlledField<M, SensorComponentType.Pump, ControlComponentType.Pump>,
) => ({
  controls: { pump: getField(ControlComponentType.Pump, module, field) },
  source: getField(SensorComponentType.Pump, module, field),
});

/** Source fields for a temperature sensor that also reports its source as the measurement. */
export const measuredTemperatureFields = (
  source: ModuleField<SensorComponentType.Temperature>,
) => ({
  sensors: { measurement: source },
  source,
});
