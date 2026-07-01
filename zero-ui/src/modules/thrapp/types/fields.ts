import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { BoilerTankStateField, MimicComponentType } from ".";
import { HeatExchangerPortOrientation } from "../mimics/components/heat-exchanger";
import { ModuleField } from "../mimics/providers";

export type ComponentFields<
  Type extends
    | ControlComponentType
    | SensorComponentType
    | ParametersType
    | ControllerStateComponentType,
> = Record<MimicComponentType, Record<string, Type>>;

export type ComponentTypeFields<
  Type extends
    | ControlComponentType
    | SensorComponentType
    | ParametersType
    | ControllerStateComponentType,
  Fields extends ComponentFields<Type>,
> = Fields;

export type SensorFields<Fields extends ComponentFields<SensorComponentType>> = ComponentTypeFields<
  SensorComponentType,
  Fields
>;

export type ControlFields<Fields extends ComponentFields<ControlComponentType>> =
  ComponentTypeFields<ControlComponentType, Fields>;

export type ControllerStateFields<Fields extends ComponentFields<ControllerStateComponentType>> =
  ComponentTypeFields<ControllerStateComponentType, Fields>;

export type ParameterFields<Fields extends ComponentFields<ParametersType>> = ComponentTypeFields<
  ParametersType,
  Fields
>;

export type SourceFields<
  Fields extends Record<
    MimicComponentType,
    SensorComponentType | ControlComponentType | ParametersType | undefined
  >,
> = Fields;

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
    flowMeasurement: SensorComponentType.Flow;
    temperatureMeasurement: SensorComponentType.Temperature;
  };
  [MimicComponentType.HeatExchanger]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    flow: SensorComponentType.Flow;
  };
  [MimicComponentType.PressureSensor]: {
    flow: SensorComponentType.Flow;
  };
  [MimicComponentType.TemperatureSensor]: {
    measurement: SensorComponentType.Temperature;
  };
  [MimicComponentType.FlowSensor]: {
    temperature: SensorComponentType.Temperature;
  };
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.ExchangeCircuit]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    flow: SensorComponentType.Flow;
    deltaT: SensorComponentType.DeltaT;
    heatExchanger: SensorComponentType.HeatExchanger;
  };
  [MimicComponentType.HotWaterCircuit]: {
    flowIn: SensorComponentType.CalculatedFlow;
    flowOut: SensorComponentType.Flow;
    tIn: SensorComponentType.Temperature;
    tOut: SensorComponentType.Temperature;
  };
  [MimicComponentType.HeatPump]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    measurement: SensorComponentType.Flow;
  };
  [MimicComponentType.HVAC]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    measurement: SensorComponentType.Flow;
  };
  [MimicComponentType.SwitchValve]: EmptyObject;
  [MimicComponentType.FlowControlValve]: {
    measurement: SensorComponentType.Flow;
  };
}>;

export type ControlFieldDefinitions = ControlFields<{
  [MimicComponentType.BoilerTank]: EmptyObject;
  [MimicComponentType.Pump]: {
    pump: ControlComponentType.Pump;
  };
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: {
    pump: ControlComponentType.Pump;
  };
  [MimicComponentType.TemperatureSensor]: {
    pump: ControlComponentType.Pump;
  };
  [MimicComponentType.FlowSensor]: {
    pump: ControlComponentType.Pump;
  };
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.HeatPump]: {
    heatpump: ControlComponentType.Heatpump;
  };
  [MimicComponentType.HVAC]: EmptyObject;
  [MimicComponentType.SwitchValve]: {
    valve: ControlComponentType.Valve;
  };
  [MimicComponentType.ExchangeCircuit]: EmptyObject;
  [MimicComponentType.HotWaterCircuit]: EmptyObject;
  [MimicComponentType.FlowControlValve]: {
    pump: ControlComponentType.Pump;
    valve: ControlComponentType.Valve;
  };
}>;

export type ControllerStateFieldDefinitions = ControllerStateFields<{
  [MimicComponentType.BoilerTank]: {
    controller: ControllerStateComponentType.DhwTanksController;
  };
  [MimicComponentType.Pump]: {
    flowController: ControllerStateComponentType.PIDController;
    temperatureController: ControllerStateComponentType.PIDController;
  };
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: {
    controller: ControllerStateComponentType.PIDController;
  };
  [MimicComponentType.TemperatureSensor]: {
    controller: ControllerStateComponentType.PIDController;
  };
  [MimicComponentType.FlowSensor]: {
    controller: ControllerStateComponentType.PIDController;
  };
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.HeatPump]: {
    controller: ControllerStateComponentType.PIDController;
  };
  [MimicComponentType.HVAC]: {
    controller: ControllerStateComponentType.PIDController;
  };
  [MimicComponentType.SwitchValve]: EmptyObject;
  [MimicComponentType.ExchangeCircuit]: EmptyObject;
  [MimicComponentType.HotWaterCircuit]: EmptyObject;
  [MimicComponentType.FlowControlValve]: {
    controller: ControllerStateComponentType.PIDController;
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
  [MimicComponentType.Pump]: {
    temperature: ParametersType.Temperature;
    flow: ParametersType.Flow;
  };
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: {
    flow: ParametersType.Flow;
  };
  [MimicComponentType.TemperatureSensor]: {
    temperature: ParametersType.Temperature;
  };
  [MimicComponentType.FlowSensor]: {
    flow: ParametersType.Flow;
  };
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.HeatPump]: {
    temperature: ParametersType.Temperature;
    flow: ParametersType.Flow;
  };
  [MimicComponentType.HVAC]: {
    temperature: ParametersType.Temperature;
    flow: ParametersType.Flow;
  };
  [MimicComponentType.SwitchValve]: EmptyObject;
  [MimicComponentType.FlowControlValve]: {
    flow: ParametersType.Flow;
  };
}>;

export type CustomFieldDefinitions = CustomFields<{
  [MimicComponentType.BoilerTank]: {
    tankStateField: BoilerTankStateField;
  };
  [MimicComponentType.Pump]: EmptyObject;
  [MimicComponentType.HeatExchanger]: {
    sideA: HeatExchangerPortOrientation;
    sideB: HeatExchangerPortOrientation;
    exchangeCircuit: ExtractSensorFields<MimicComponentType.ExchangeCircuit>["sensors"];
  };
  [MimicComponentType.ExchangeCircuit]: {
    width?: number | string;
    height?: number | string;
    forceHeight?: boolean;
    circuitName: string;
  };
  [MimicComponentType.HotWaterCircuit]: {
    width?: number | string;
    height?: number | string;
  };
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.HeatPump]: EmptyObject;
  [MimicComponentType.HVAC]: EmptyObject;
  [MimicComponentType.SwitchValve]: {
    tank?: {
      operator?: ExtractSensorFields<MimicComponentType.BoilerTank>["sensors"];
      operatorName?: string;
      controller?: ModuleField<ControllerStateComponentType.DhwTanksController>;
    };
  };
  [MimicComponentType.FlowControlValve]: EmptyObject;
}>;

export type SourceFieldDefinitions = SourceFields<{
  [MimicComponentType.Pump]: SensorComponentType.Pump;
  [MimicComponentType.HeatExchanger]: SensorComponentType.HeatExchanger;
  [MimicComponentType.PressureSensor]: SensorComponentType.Pressure;
  [MimicComponentType.TemperatureSensor]: SensorComponentType.Temperature;
  [MimicComponentType.FlowSensor]: SensorComponentType.Flow;
  [MimicComponentType.ManualValve]: undefined;
  [MimicComponentType.HeatPump]: SensorComponentType.HeatExchanger;
  [MimicComponentType.HVAC]: SensorComponentType.HeatExchanger;
  [MimicComponentType.SwitchValve]: SensorComponentType.Valve;
  [MimicComponentType.FlowControlValve]: SensorComponentType.Valve;
  [MimicComponentType.BoilerTank]: undefined;
  [MimicComponentType.ExchangeCircuit]: undefined;
  [MimicComponentType.HotWaterCircuit]: undefined;
}>;

export type ExtractModuleFields<
  Fields extends Record<
    string,
    SensorComponentType | ControlComponentType | ParametersType | ControllerStateComponentType
  >,
> = { [K in keyof Fields]: ModuleField<Fields[K]> };

export type ExtractComponentFields<Type extends MimicComponentType> = ExtractSensorFields<Type> &
  ExtractControlFields<Type> &
  ExtractParameterFields<Type> &
  ExtractCustomFields<Type> &
  ExtractSourceFields<Type> &
  ExtractControllerStateFields<Type>;

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const EMPTY_OBJECT = {};
type EmptyObject = typeof EMPTY_OBJECT;

export type ExtractSensorFields<Type extends MimicComponentType> = {
  sensors: ExtractModuleFields<SensorFieldDefinitions[Type]>;
};

export type ExtractControlFields<Type extends MimicComponentType> = {
  controls: ExtractModuleFields<ControlFieldDefinitions[Type]>;
};
export type ExtractControllerStateFields<Type extends MimicComponentType> = {
  controllerState: ExtractModuleFields<ControllerStateFieldDefinitions[Type]>;
};

export type ExtractParameterFields<Type extends MimicComponentType> = {
  parameters: ExtractModuleFields<ParameterFieldDefinitions[Type]>;
};

export type ExtractCustomFields<Type extends MimicComponentType> = {
  custom: CustomFieldDefinitions[Type];
};

export type ExtractSourceFields<Type extends MimicComponentType> = {
  source: SourceFieldDefinitions[Type] extends undefined
    ? undefined
    : ModuleField<SourceFieldDefinitions[Type]>;
};
