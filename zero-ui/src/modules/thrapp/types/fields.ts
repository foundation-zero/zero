import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { type Component } from "vue";
import { BoilerTankStateField, MimicComponentType } from ".";
import { HeatExchangerPortOrientation } from "../mimics/components/heat-exchanger";
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
    pressure: SensorComponentType.Pressure;
    pump: SensorComponentType.Pump;
    flowMeasurement: SensorComponentType.Flow;
    temperatureMeasurement: SensorComponentType.Temperature;
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
  [MimicComponentType.ExchangeCircuit]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    flow: SensorComponentType.Flow;
    deltaT: SensorComponentType.DeltaT;
  };
  [MimicComponentType.HotWaterCircuit]: {
    flowIn: SensorComponentType.CalculatedFlow;
    flowOut: SensorComponentType.Flow;
    tIn: SensorComponentType.Temperature;
    tOut: SensorComponentType.Temperature;
  };
  [MimicComponentType.Asset]: {
    heatExchanger: SensorComponentType.HeatExchanger;
  };
  [MimicComponentType.SwitchValve]: {
    valve: SensorComponentType.Valve;
  };
  [MimicComponentType.FlowControlValve]: {
    valve: SensorComponentType.Valve;
    measurement: SensorComponentType.Temperature;
  };
}>;

export type ControlFieldDefinitions = ControlFields<{
  [MimicComponentType.BoilerTank]: {
    controller: ControlComponentType.BoilersTanksController;
  };
  [MimicComponentType.Pump]: {
    flowController: ControlComponentType.PIDController;
    temperatureController: ControlComponentType.PIDController;
    pump: ControlComponentType.Pump;
  };
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.Asset]: EmptyObject;
  [MimicComponentType.SwitchValve]: {
    valve: ControlComponentType.Valve;
  };
  [MimicComponentType.ExchangeCircuit]: EmptyObject;
  [MimicComponentType.HotWaterCircuit]: EmptyObject;
  [MimicComponentType.FlowControlValve]: {
    valve: ControlComponentType.Valve;
    controller: ControlComponentType.PIDController;
  };
}>;

export type ParameterFieldDefinitions = ParameterFields<{
  [MimicComponentType.BoilerTank]: {
    minimumLevel: ParametersType.Level;
    maximumLevel: ParametersType.Level;
    minimumTemperature: ParametersType.Temperature;
    maximumTemperature: ParametersType.Temperature;
  };
  [MimicComponentType.ExchangeCircuit]: EmptyObject;
  [MimicComponentType.HotWaterCircuit]: EmptyObject;
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
  [MimicComponentType.Pump]: {
    flowSetpointName: string;
    temperatureSetpointName: string;
  };
  [MimicComponentType.HeatExchanger]: {
    sideA: HeatExchangerPortOrientation;
    sideB: HeatExchangerPortOrientation;
    circuit: ExtractSensorFields<MimicComponentType.ExchangeCircuit>["sensors"];
    exchangeCircuit: ExtractSensorFields<MimicComponentType.ExchangeCircuit>["sensors"];
  };
  [MimicComponentType.ExchangeCircuit]: {
    width?: number | string;
    height?: number | string;
    forceHeight?: boolean;
  };
  [MimicComponentType.HotWaterCircuit]: {
    width?: number | string;
    height?: number | string;
  };
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.Asset]: {
    icon: Component;
    width?: number | string;
    height?: number | string;
    hideMode?: boolean;
  };
  [MimicComponentType.SwitchValve]: {
    tank?: {
      operator?: ExtractSensorFields<MimicComponentType.BoilerTank>["sensors"];
      operatorName?: string;
      controller?: ModuleField<ControlComponentType.BoilersTanksController>;
    };
  };
  [MimicComponentType.FlowControlValve]: {
    controllerName: string;
    setpointName: string;
  };
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
