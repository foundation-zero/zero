import { DhwTankController } from "@/modules/thrs/types";

export const enum MimicComponentType {
  ExchangeCircuit = "ExchangeCircuit",
  HotWaterCircuit = "HotWaterCircuit",
  HeatPump = "HeatPump",
  HVAC = "HVAC",
  SwitchValve = "SwitchValve",
  FlowControlValve = "FlowControlValve",
  HeatExchanger = "HeatExchanger",
  BoilerTank = "BoilerTank",
  Pump = "Pump",
  ManualPump = "ManualPump",
  PressureSensor = "PressureSensor",
  PressureGauge = "PressureGauge",
  TemperatureSensor = "TemperatureSensor",
  FlowSensor = "FlowSensor",
  ManualValve = "ManualValve",
  MixValve = "MixValve",
  CheckValve = "CheckValve",
  ThreeWaySwitchValve = "ThreeWaySwitchValve",
  LevelSensor = "LevelSensor",
  LevelSwitch = "LevelSwitch",
}

export type BoilerTankStateField = keyof Omit<DhwTankController, "timeToFill">;
