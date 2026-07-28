import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { BoilerTankStateField, MimicComponentType } from ".";
import { TooltipComponentContext } from "../components/tooltip";
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
  };
  [MimicComponentType.HeatExchanger]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    flow: SensorComponentType.Flow;
  };
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.PressureGauge]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.LevelSensor]: EmptyObject;
  [MimicComponentType.LevelSwitch]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.MixValve]: EmptyObject;
  [MimicComponentType.CheckValve]: EmptyObject;
  [MimicComponentType.ThreeWaySwitchValve]: EmptyObject;
  [MimicComponentType.ExchangeCircuit]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    flow: SensorComponentType.Flow;
    deltaT: SensorComponentType.DeltaT;
    heatExchanger: SensorComponentType.HeatExchanger;
  };
  [MimicComponentType.HotWaterCircuit]: {
    flowIn: SensorComponentType.Flow | SensorComponentType.CalculatedFlow;
    flowOut: SensorComponentType.Flow | SensorComponentType.CalculatedFlow;
    tIn: SensorComponentType.Temperature;
    tOut: SensorComponentType.Temperature;
  };
  [MimicComponentType.HeatPump]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
  };
  [MimicComponentType.HVAC]: {
    incoming: SensorComponentType.Temperature;
    outgoing: SensorComponentType.Temperature;
    flow: SensorComponentType.Flow;
  };
  [MimicComponentType.SwitchValve]: EmptyObject;
  [MimicComponentType.FlowControlValve]: EmptyObject;
}>;

export type ControlFieldDefinitions = ControlFields<{
  [MimicComponentType.BoilerTank]: EmptyObject;
  [MimicComponentType.Pump]: {
    pump: ControlComponentType.Pump;
  };
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.PressureGauge]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.LevelSensor]: EmptyObject;
  [MimicComponentType.LevelSwitch]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.MixValve]: {
    valve: ControlComponentType.Valve;
  };
  [MimicComponentType.CheckValve]: EmptyObject;
  [MimicComponentType.ThreeWaySwitchValve]: {
    valve: ControlComponentType.Valve;
  };
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
    valve: ControlComponentType.Valve;
  };
}>;

export type ControllerStateFieldDefinitions = ControllerStateFields<{
  [MimicComponentType.BoilerTank]: {
    controller: ControllerStateComponentType.DhwTanksController;
  };
  [MimicComponentType.Pump]: EmptyObject;
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.PressureGauge]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.LevelSensor]: EmptyObject;
  [MimicComponentType.LevelSwitch]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.MixValve]: {
    controller?: ControllerStateComponentType.PIDController;
  };
  [MimicComponentType.CheckValve]: EmptyObject;
  [MimicComponentType.ThreeWaySwitchValve]: EmptyObject;
  [MimicComponentType.HeatPump]: EmptyObject;
  [MimicComponentType.HVAC]: EmptyObject;
  [MimicComponentType.SwitchValve]: EmptyObject;
  [MimicComponentType.ExchangeCircuit]: EmptyObject;
  [MimicComponentType.HotWaterCircuit]: EmptyObject;
  [MimicComponentType.FlowControlValve]: EmptyObject;
}>;

export type ParameterFieldDefinitions = ParameterFields<{
  [MimicComponentType.BoilerTank]: {
    minimumLevel: ParametersType.Level;
    maximumLevel: ParametersType.Level;
    minimumTemperature: ParametersType.Temperature;
    maximumTemperature: ParametersType.Temperature;
    disabled: ParametersType.Disabled;
  };
  [MimicComponentType.ExchangeCircuit]: EmptyObject;
  [MimicComponentType.HotWaterCircuit]: EmptyObject;
  [MimicComponentType.Pump]: EmptyObject;
  [MimicComponentType.HeatExchanger]: EmptyObject;
  [MimicComponentType.PressureSensor]: EmptyObject;
  [MimicComponentType.PressureGauge]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: EmptyObject;
  [MimicComponentType.FlowSensor]: EmptyObject;
  [MimicComponentType.LevelSensor]: EmptyObject;
  [MimicComponentType.LevelSwitch]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.MixValve]: EmptyObject;
  [MimicComponentType.CheckValve]: EmptyObject;
  [MimicComponentType.ThreeWaySwitchValve]: EmptyObject;
  [MimicComponentType.HeatPump]: EmptyObject;
  [MimicComponentType.HVAC]: EmptyObject;
  [MimicComponentType.SwitchValve]: EmptyObject;
  [MimicComponentType.FlowControlValve]: EmptyObject;
}>;

export type PIDController<
  Type extends SensorComponentType.Temperature | SensorComponentType.Flow =
    | SensorComponentType.Temperature
    | SensorComponentType.Flow,
  Parameter extends ParametersType = Type extends SensorComponentType.Temperature
    ? ParametersType.Temperature
    : ParametersType.Flow | ParametersType.FlowControl,
> = {
  type: Type;
  controller: ModuleField<ControllerStateComponentType.PIDController>;
  measurement?: ModuleField<Type>;
  actuator?: ModuleField;
  setpoint?: ModuleField<Parameter>;
  outputMinimum?: ModuleField<ParametersType>;
};

export type BoilerTankController = TooltipComponentContext<MimicComponentType.BoilerTank>;

export type CustomFieldDefinitions = CustomFields<{
  [MimicComponentType.BoilerTank]: {
    tankStateField: BoilerTankStateField;
  };
  [MimicComponentType.Pump]: {
    flowController: PIDController<SensorComponentType.Flow>;
    temperatureController: PIDController<SensorComponentType.Flow>;
  };
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
  [MimicComponentType.PressureSensor]: {
    controller?: PIDController;
  };
  [MimicComponentType.PressureGauge]: EmptyObject;
  [MimicComponentType.TemperatureSensor]: {
    controller?: PIDController;
  };
  [MimicComponentType.FlowSensor]: {
    controller?: PIDController;
  };
  [MimicComponentType.LevelSensor]: EmptyObject;
  [MimicComponentType.LevelSwitch]: EmptyObject;
  [MimicComponentType.ManualValve]: EmptyObject;
  [MimicComponentType.MixValve]: EmptyObject;
  [MimicComponentType.CheckValve]: EmptyObject;
  [MimicComponentType.ThreeWaySwitchValve]: EmptyObject;
  [MimicComponentType.HeatPump]: {
    controller?: PIDController;
  };
  [MimicComponentType.HVAC]: EmptyObject;
  [MimicComponentType.SwitchValve]: {
    tankController?: BoilerTankController;
  };
  [MimicComponentType.FlowControlValve]: {
    controller?: PIDController;
  };
}>;

export type SourceFieldDefinitions = SourceFields<{
  [MimicComponentType.Pump]: SensorComponentType.Pump;
  [MimicComponentType.HeatExchanger]: SensorComponentType.HeatExchanger;
  [MimicComponentType.PressureSensor]: SensorComponentType.Pressure;
  [MimicComponentType.PressureGauge]: undefined;
  [MimicComponentType.TemperatureSensor]: SensorComponentType.Temperature;
  [MimicComponentType.FlowSensor]: SensorComponentType.Flow;
  [MimicComponentType.LevelSensor]: SensorComponentType.Level;
  [MimicComponentType.LevelSwitch]: SensorComponentType.LevelSwitch;
  [MimicComponentType.ManualValve]: undefined;
  [MimicComponentType.MixValve]: SensorComponentType.Valve;
  [MimicComponentType.CheckValve]: undefined;
  [MimicComponentType.ThreeWaySwitchValve]: SensorComponentType.Valve;
  [MimicComponentType.HeatPump]: SensorComponentType.HeatExchanger;
  [MimicComponentType.HVAC]: SensorComponentType.HeatExchanger;
  [MimicComponentType.SwitchValve]: SensorComponentType.Valve;
  [MimicComponentType.FlowControlValve]: SensorComponentType.Valve;
  [MimicComponentType.BoilerTank]: undefined;
  [MimicComponentType.ExchangeCircuit]: undefined;
  [MimicComponentType.HotWaterCircuit]: undefined;
}>;

export type Defined<P, T extends P | undefined> = T extends P ? T : P;

export type ExtractModuleFields<
  Fields extends Record<
    string,
    SensorComponentType | ControlComponentType | ParametersType | ControllerStateComponentType
  >,
> = {
  [K in keyof Fields]: Fields[K] extends undefined
    ? ModuleField<Fields[K]> | undefined
    : ModuleField<Fields[K]>;
};

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
    ? ModuleField<"custom"> | undefined
    : ModuleField<SourceFieldDefinitions[Type]>;
};
