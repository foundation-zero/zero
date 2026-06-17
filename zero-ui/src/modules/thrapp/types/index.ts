import { BoilerTankController } from "@/modules/thrs/types";

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
  TemperatureSensor = "TemperatureSensor",
  FlowSensor = "FlowSensor",
  ManualValve = "ManualValve",
}

export type BoilerTankStateField = keyof Omit<BoilerTankController, "timeToFill">;
