import {
  ControlComponentType,
  ControlDefinitionMap,
  SensorComponentType,
  SensorDefinitionMap,
} from "@/modules/thrapp/types/thrs";

export const DEFAULT_SENSOR_FIELD_VALUE_FIELD: {
  [Type in SensorComponentType]: keyof SensorDefinitionMap[Type];
} = {
  [SensorComponentType.Temperature]: "temperature",
  [SensorComponentType.CalculatedTemperature]: "temperature",
  [SensorComponentType.Pressure]: "pressure",
  [SensorComponentType.Flow]: "flow",
  [SensorComponentType.FlowOnly]: "flow",
  [SensorComponentType.Pump]: "flow",
  [SensorComponentType.Valve]: "positionRel",
  [SensorComponentType.Thruster]: "active",
  [SensorComponentType.Pcs]: "mode",
  [SensorComponentType.Level]: "level",
  [SensorComponentType.LevelSwitch]: "empty",
  [SensorComponentType.HeatTransferDevice]: "deltaT",
  [SensorComponentType.HeatPump]: "on",
  [SensorComponentType.Pvt]: "power",
  [SensorComponentType.CalculatedFlow]: "flow",
  [SensorComponentType.AdsorptionChiller]: "operating",
  [SensorComponentType.Brightloop]: "active",
  [SensorComponentType.BrightloopConverter]: "active",
  [SensorComponentType.Ugrid]: "active",
  [SensorComponentType.PropulsionDrive]: "active",
  [SensorComponentType.ShorePowerConverter]: "active",
  [SensorComponentType.BrightloopGroup]: "anyActive",
  [SensorComponentType.UgridGroup]: "anyActive",
  [SensorComponentType.ShorePowerGroup]: "anyActive",
  [SensorComponentType.Pyranometer]: "irradiance",
  [SensorComponentType.AmcsControlMode]: "mode",
};

export const DEFAULT_CONTROL_FIELD_VALUE_FIELD: {
  [Type in ControlComponentType]: keyof ControlDefinitionMap[Type];
} = {
  [ControlComponentType.Pump]: "dutypoint",
  [ControlComponentType.Valve]: "setpoint",
  [ControlComponentType.Pcm]: "on",
  [ControlComponentType.Heatpump]: "on",
  [ControlComponentType.AdsorptionChiller]: "enable",
};
