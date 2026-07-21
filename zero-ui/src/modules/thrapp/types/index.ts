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
  PressureSensor = "PressureSensor",
  PressureGauge = "PressureGauge",
  TemperatureSensor = "TemperatureSensor",
  FlowSensor = "FlowSensor",
  ManualValve = "ManualValve",
  LevelSensor = "LevelSensor",
}

export type BoilerTankStateField = keyof Omit<DhwTankController, "timeToFill">;
