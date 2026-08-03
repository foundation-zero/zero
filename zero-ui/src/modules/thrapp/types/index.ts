import { DhwTankController } from "@/modules/thrsim/types";

export const enum MimicComponentType {
  ExchangeCircuit = "ExchangeCircuit",
  FreshwaterCircuit = "FreshwaterCircuit",
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
  Pvt = "Pvt",
}

export type BoilerTankStateField = keyof Omit<DhwTankController, "timeToFill">;
