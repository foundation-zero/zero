export const THRUSTERS_CONTROL_QUERY = `
  thrustersPump1 {
      dutypoint { value timestamp }
      on { value timestamp }
      }
  thrustersPump2 {
      dutypoint { value timestamp }
      on { value timestamp }
      }
  thrustersMixRecovery {
      setpoint { value timestamp }
      }
  thrustersMixExchanger {
      setpoint { value timestamp }
      }
  thrustersFlowcontrolAft {
      setpoint { value timestamp }
      }
  thrustersFlowcontrolFwd {
      setpoint { value timestamp }
      }
  thrustersShutoffRecovery {
      setpoint { value timestamp }
      }
  thrustersSwitchAft {
      setpoint { value timestamp }
      }
  thrustersSwitchFwd {
      setpoint { value timestamp }
      }
`;

export const THRUSTERS_SENSOR_QUERY = `
  thrustersPump1 {
      flow { value timestamp }
      speed { value timestamp }
      opTime { value timestamp }
      }
  thrustersPump2 {
      flow { value timestamp }
      speed { value timestamp }
      opTime { value timestamp }
      }
  thrustersTemperatureAftReturn {
      temperature { value timestamp }
      }
  thrustersTemperatureFwdReturn {
      temperature { value timestamp }
      }
  thrustersTemperatureSupply {
      temperature { value timestamp }
      }
  thrustersTemperatureRecoveryMix {
      temperature { value timestamp }
      }
  thrustersMixRecovery {
      positionRel { value timestamp }
      }
  thrustersMixExchanger {
      positionRel { value timestamp }
      }
  thrustersFlowFwd {
      flow { value timestamp }
      temperature { value timestamp }
      }
  thrustersFlowAft {
      flow { value timestamp }
      temperature { value timestamp }
      }
  thrustersFlowcontrolAft {
      positionRel { value timestamp }
      }
  thrustersFlowcontrolFwd {
      positionRel { value timestamp }
      }
  thrustersShutoffRecovery {
      positionRel { value timestamp }
      }
  thrustersSwitchAft {
      positionRel { value timestamp }
      }
  thrustersSwitchFwd {
      positionRel { value timestamp }
      }
  thrustersFlowRecovery {
      flow { value timestamp }
      temperature { value timestamp }
      }
  thrustersPressurePump {
      pressure { value timestamp }
      }
  thrustersPressureRelief {
      pressure { value timestamp }
      }
  thrustersAft {
      active { value timestamp }
      }
  thrustersFwd {
      active { value timestamp }
      }
  thrustersPcs {
      mode { value timestamp }
      }
`;

export const THRUSTERS_PARAMETERS_QUERY = `
  maximumSupplyTemperature
  coolingTemperature
  coolingFlow
  recoveryTemperature
  warmupTemperature
  thrustersMinimumFlow
  thrustersMaximumFlow
  pumpTuning
  warmupMixTuning
  heatDumpTuning
  aftFlowBalanceTuning
  fwdFlowBalanceTuning
  aftTemperatureTuning
  fwdTemperatureTuning
`;
