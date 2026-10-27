import { ManualValveType } from "../../mimics/components/manual-valve";
import { MimicKey } from "../../router/mimics";
import { MimicComponentType } from "../../types";

/** Legend entries that are not tied to a mimic component type. */
export const enum LegendFeature {
  AnimatedFlows = "AnimatedFlows",
  SectionArea = "SectionArea",
}

export type LegendSubType = {
  [MimicComponentType.ManualValve]: [
    ManualValveType.Flow,
    ManualValveType.Switch,
    ManualValveType.FlowControl,
    ManualValveType.ThreeWay,
  ];
};

export type LegendMap = {
  [Type in MimicComponentType]?:
    true | (Type extends keyof LegendSubType ? LegendSubType[Type][number][] : never);
} & {
  [Feature in LegendFeature]?: true;
};

export type LegendKey = keyof LegendMap;

/** Whether a legend entry (optionally a specific sub type) is used by the mimic. */
export const isInLegend = <Key extends LegendKey>(
  legend: LegendMap,
  key: Key,
  subType?: Key extends keyof LegendSubType ? LegendSubType[Key][number] : never,
) => {
  const entry = legend[key];

  if (entry === undefined) return false;
  if (subType === undefined || entry === true) return true;

  return (entry as string[]).includes(subType);
};

export const MIMIC_LEGEND_MAP: Partial<Record<MimicKey, LegendMap>> = {
  dhw: {
    [MimicComponentType.ExchangeCircuit]: true,
    [MimicComponentType.FreshwaterCircuit]: true,
    [MimicComponentType.HeatPump]: true,
    [MimicComponentType.HVAC]: true,
    [MimicComponentType.BoilerTank]: true,
    [MimicComponentType.SwitchValve]: true,
    [MimicComponentType.FlowControlValve]: true,
    [MimicComponentType.HeatExchanger]: true,
    [MimicComponentType.Pump]: true,
    [MimicComponentType.TemperatureSensor]: true,
    [MimicComponentType.FlowSensor]: true,
    [MimicComponentType.PressureSensor]: true,
    [MimicComponentType.LevelSensor]: true,
    [MimicComponentType.LevelSwitch]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch],
    [MimicComponentType.PressureGauge]: true,
    [LegendFeature.AnimatedFlows]: true,
    [LegendFeature.SectionArea]: true,
  },
  thrusters: {
    [MimicComponentType.ConnectingCircuit]: true,
    [MimicComponentType.SeawaterCircuit]: true,
    [MimicComponentType.Thruster]: true,
    [MimicComponentType.ExpansionTank]: true,
    [MimicComponentType.SwitchValve]: true,
    [MimicComponentType.FlowControlValve]: true,
    [MimicComponentType.MixValve]: true,
    [MimicComponentType.ThreeWaySwitchValve]: true,
    [MimicComponentType.HeatExchanger]: true,
    [MimicComponentType.Pump]: true,
    [MimicComponentType.TemperatureSensor]: true,
    [MimicComponentType.FlowSensor]: true,
    [MimicComponentType.PressureSensor]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch],
    [MimicComponentType.PressureGauge]: true,
    [MimicComponentType.CheckValve]: true,
    [MimicComponentType.ExpansionValve]: true,
    [LegendFeature.SectionArea]: true,
  },
  pvt: {
    [MimicComponentType.ConnectingCircuit]: true,
    [MimicComponentType.SeawaterCircuit]: true,
    [MimicComponentType.Pvt]: true,
    [MimicComponentType.ExpansionTank]: true,
    [MimicComponentType.SwitchValve]: true,
    [MimicComponentType.MixValve]: true,
    [MimicComponentType.HeatExchanger]: true,
    [MimicComponentType.Pump]: true,
    [MimicComponentType.ManualPump]: true,
    [MimicComponentType.TemperatureSensor]: true,
    [MimicComponentType.FlowSensor]: true,
    [MimicComponentType.PressureSensor]: true,
    [MimicComponentType.Pyranometer]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch],
    [MimicComponentType.PressureGauge]: true,
    [MimicComponentType.CheckValve]: true,
    [MimicComponentType.ExpansionValve]: true,
    [LegendFeature.SectionArea]: true,
  },
  pcm: {
    [MimicComponentType.ExchangeCircuit]: true,
    [MimicComponentType.ConnectingCircuit]: true,
    [MimicComponentType.Pcm]: true,
    [MimicComponentType.AirTrapVessel]: true,
    [MimicComponentType.SwitchValve]: true,
    [MimicComponentType.FlowControlValve]: true,
    [MimicComponentType.HeatExchanger]: true,
    [MimicComponentType.Pump]: true,
    [MimicComponentType.TemperatureSensor]: true,
    [MimicComponentType.FlowSensor]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch],
    [MimicComponentType.PressureGauge]: true,
    [MimicComponentType.CheckValve]: true,
  },
  dc: {
    [MimicComponentType.ExchangeCircuit]: true,
    [MimicComponentType.SeawaterCircuit]: true,
    [MimicComponentType.DcConverter]: true,
    [MimicComponentType.ExpansionTank]: true,
    [MimicComponentType.MixValve]: true,
    [MimicComponentType.HeatExchanger]: true,
    [MimicComponentType.Pump]: true,
    [MimicComponentType.TemperatureSensor]: true,
    [MimicComponentType.FlowSensor]: true,
    [MimicComponentType.PressureSensor]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch],
    [MimicComponentType.PressureGauge]: true,
    [MimicComponentType.CheckValve]: true,
    [MimicComponentType.ExpansionValve]: true,
  },
  drives: {
    [MimicComponentType.ExchangeCircuit]: true,
    [MimicComponentType.SeawaterCircuit]: true,
    [MimicComponentType.PropulsionDrive]: true,
    [MimicComponentType.PropulsionCooler]: true,
    [MimicComponentType.ShorePowerConverter]: true,
    [MimicComponentType.ExpansionTank]: true,
    [MimicComponentType.SwitchValve]: true,
    [MimicComponentType.FlowControlValve]: true,
    [MimicComponentType.MixValve]: true,
    [MimicComponentType.HeatExchanger]: true,
    [MimicComponentType.Pump]: true,
    [MimicComponentType.TemperatureSensor]: true,
    [MimicComponentType.FlowSensor]: true,
    [MimicComponentType.PressureSensor]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch, ManualValveType.Flow],
    [MimicComponentType.PressureGauge]: true,
    [MimicComponentType.CheckValve]: true,
    [MimicComponentType.ExpansionValve]: true,
  },
  "pvt-owners": {
    [MimicComponentType.ConnectingCircuit]: true,
    [MimicComponentType.TemperatureSensor]: true,
    [MimicComponentType.FlowSensor]: true,
    [MimicComponentType.ManualValve]: [ManualValveType.Switch],
  },
};
