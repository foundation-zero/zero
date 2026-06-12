import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { BoilerTankStateField, MimicComponentType } from ".";
import { ModuleField } from "../mimics/providers";

export type ComponentFields<
  Type extends ControlComponentType | SensorComponentType | ParametersType,
> = Record<MimicComponentType, Record<string, Type>>;

export type ComponentTypeFields<
  Type extends ControlComponentType | SensorComponentType | ParametersType,
  Fields extends ComponentFields<Type>,
> = Fields;

export type SensorFields<Fields extends ComponentFields<SensorComponentType>> = ComponentTypeFields<
  SensorComponentType,
  Fields
>;

export type ControlFields<Fields extends ComponentFields<ControlComponentType>> =
  ComponentTypeFields<ControlComponentType, Fields>;

export type ParameterFields<Fields extends ComponentFields<ParametersType>> = ComponentTypeFields<
  ParametersType,
  Fields
>;

export type CustomFields<Fields extends Record<MimicComponentType, Record<string, unknown>>> =
  Fields;

export type SensorFieldDefinitions = SensorFields<{
  [MimicComponentType.BoilerTank]: {
    level: SensorComponentType.Level;
    temperature: SensorComponentType.Temperature;
    boostSupplyValve: SensorComponentType.Valve;
    boostReturnValve: SensorComponentType.Valve;
    supplyValve: SensorComponentType.Valve;
    dischargeValve: SensorComponentType.Valve;
    boostingSupply: SensorComponentType.Temperature;
  };
  [MimicComponentType.Pump]: {
    pump: SensorComponentType.Pump;
  };
  [MimicComponentType.HeatExchanger]: {
    heatExchanger: SensorComponentType.HeatExchanger;
  };
  [MimicComponentType.PressureSensor]: {
    pressure: SensorComponentType.Pressure;
  };
  [MimicComponentType.TemperatureSensor]: {
    temperature: SensorComponentType.Temperature;
  };
  [MimicComponentType.FlowSensor]: {
    flow: SensorComponentType.Flow;
  };
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.Asset]: {
    heatExchanger: SensorComponentType.HeatExchanger;
  };
  [MimicComponentType.SwitchValve]: {
    valve: SensorComponentType.Valve;
  };
  [MimicComponentType.FlowControlValve]: {
    valve: SensorComponentType.Valve;
  };
}>;

export type ControlFieldDefinitions = ControlFields<{
  [MimicComponentType.BoilerTank]: {
    controller: ControlComponentType.BoilersTanksController;
  };
  [MimicComponentType.Pump]: EmptyObject;
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.Asset]: EmptyObject;
  [MimicComponentType.SwitchValve]: {
    valve: ControlComponentType.Valve;
  };
  [MimicComponentType.FlowControlValve]: EmptyObject;
}>;

export type ParameterFieldDefinitions = ParameterFields<{
  [MimicComponentType.BoilerTank]: {
    minimumLevel: ParametersType.Level;
    maximumLevel: ParametersType.Level;
    minimumTemperature: ParametersType.Temperature;
    maximumTemperature: ParametersType.Temperature;
  };
  [MimicComponentType.Pump]: EmptyObject;
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.Asset]: EmptyObject;
  [MimicComponentType.SwitchValve]: EmptyObject;
  [MimicComponentType.FlowControlValve]: EmptyObject;
}>;

export type CustomFieldDefinitions = CustomFields<{
  [MimicComponentType.BoilerTank]: {
    tankStateField: BoilerTankStateField;
  };
  [MimicComponentType.Pump]: EmptyObject;
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.Asset]: EmptyObject;
  [MimicComponentType.SwitchValve]: {
    tank?: {
      operator?: ExtractSensorFields<MimicComponentType.BoilerTank>["sensors"];
      operatorName?: string;
      controller?: ModuleField<ControlComponentType.BoilersTanksController>;
    };
  };
  [MimicComponentType.FlowControlValve]: EmptyObject;
}>;

export type ExtractModuleFields<
  Fields extends Record<string, SensorComponentType | ControlComponentType | ParametersType>,
> = { [K in keyof Fields]: ModuleField<Fields[K]> };

export type ExtractComponentFields<Type extends MimicComponentType> = ExtractSensorFields<Type> &
  ExtractControlFields<Type> &
  ExtractParameterFields<Type> &
  ExtractCustomFields<Type>;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const EMPTY_OBJECT = {};
type EmptyObject = typeof EMPTY_OBJECT;

export type ExtractSensorFields<Type extends MimicComponentType> = {
  sensors: ExtractModuleFields<SensorFieldDefinitions[Type]>;
};

export type ExtractControlFields<Type extends MimicComponentType> = {
  controls: ExtractModuleFields<ControlFieldDefinitions[Type]>;
};

export type ExtractParameterFields<Type extends MimicComponentType> = {
  parameters: ExtractModuleFields<ParameterFieldDefinitions[Type]>;
};

export type ExtractCustomFields<Type extends MimicComponentType> = {
  custom: CustomFieldDefinitions[Type];
};
