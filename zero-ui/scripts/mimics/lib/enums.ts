export const SENSOR_MEMBER_TO_FIELD_TYPE: Record<string, string> = {
  Temperature: "sensor:temperature",
  CalculatedTemperature: "sensor:calculatedTemperature",
  Pressure: "sensor:pressure",
  Flow: "sensor:flow",
  Pump: "sensor:pump",
  Valve: "sensor:valve",
  Thruster: "sensor:thruster",
  Pcs: "sensor:pcs",
  Pcm: "sensor:pcm",
  Level: "sensor:level",
  LevelSwitch: "sensor:levelSwitch",
  DeltaT: "sensor:deltaT",
  HeatExchanger: "sensor:heatExchanger",
  CalculatedFlow: "sensor:calculatedFlow",
  AdsorptionChiller: "sensor:adsorptionChiller",
  Brightloop: "sensor:brightloop",
  Ugrid: "sensor:ugrid",
  PropulsionDrive: "sensor:propulsionDrive",
  ShorePowerConverter: "sensor:shorePowerConverter",
};

const CONTROL_MEMBER_TO_FIELD_TYPE: Record<string, string> = {
  Pump: "control:pump",
  Valve: "control:valve",
  Pcm: "control:pcm",
  Heatpump: "control:heatpump",
  AdsorptionChiller: "control:adsorptionChiller",
};

const PARAMETER_MEMBER_TO_FIELD_TYPE: Record<string, string> = {
  Temperature: "parameter:temperature",
  Flow: "parameter:flow",
  FlowControl: "parameter:flowcontrol",
  Tuning: "parameter:tuning",
  Enabled: "parameter:enabled",
  Ratio: "parameter:ratio",
  Dutypoint: "parameter:dutypoint",
  dT: "parameter:dT",
  Level: "parameter:level",
};

const CONTROLLER_MEMBER_TO_FIELD_TYPE: Record<string, string> = {
  DhwTanksController: "controller:dhwTanksController",
  PIDController: "pidController",
};

export const NAMESPACE_TO_FIELD_TYPE: Record<string, Record<string, string>> = {
  SensorComponentType: SENSOR_MEMBER_TO_FIELD_TYPE,
  ControlComponentType: CONTROL_MEMBER_TO_FIELD_TYPE,
  ParametersType: PARAMETER_MEMBER_TO_FIELD_TYPE,
  ControllerStateComponentType: CONTROLLER_MEMBER_TO_FIELD_TYPE,
};

export const FIELD_TYPE_TO_ENUM: Record<string, { namespace: string; member: string }> =
  Object.fromEntries(
    Object.entries(NAMESPACE_TO_FIELD_TYPE).flatMap(([namespace, members]) =>
      Object.entries(members).map(([member, fieldType]) => [fieldType, { namespace, member }]),
    ),
  );

export const enumMemberOf = (fieldType: string): string =>
  FIELD_TYPE_TO_ENUM[fieldType]?.member ?? fieldType.split(":")[1] ?? fieldType;
