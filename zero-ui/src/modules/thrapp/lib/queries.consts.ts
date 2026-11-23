import { gql, TypedDocumentNode } from "@urql/vue";
import { ControlledModule } from "./consts";
import * as F from "./mqtt-graphql-queries.generated";

// Queries per view on the MQTT GraphQL API, holding only the module parts the view shows. A
// device shown in a module's view may live in another module (by its topic), so that module's
// part is queried too: `pcmTemperatureProducersSupply` in pcm, the fresh water sensors in
// freshWaterHot, the cooling devices in cooling, the drives in propulsionDrive, the shore power
// converters in dc700VShoreConverter and the uGrids in dcAcConverter.

// Mimics

export const DHW_MIMIC_QUERY = gql`
  query DhwMimic {
    ...DhwSensorValues
    ...DhwControlValues
    ...DhwParameters
    ...DhwControllerState
    ...AdsorptionSensorValues
    ...ConsumersSensorValues
    ...DcSensorValues
    ...DrivesSensorValues
    ...FreshWaterHotSensorValues
  }
  ${F.DHW_SENSOR_VALUES_FRAGMENT}
  ${F.DHW_CONTROL_VALUES_FRAGMENT}
  ${F.DHW_PARAMETERS_FRAGMENT}
  ${F.DHW_CONTROLLER_STATE_FRAGMENT}
  ${F.ADSORPTION_SENSOR_VALUES_FRAGMENT}
  ${F.CONSUMERS_SENSOR_VALUES_FRAGMENT}
  ${F.DC_SENSOR_VALUES_FRAGMENT}
  ${F.DRIVES_SENSOR_VALUES_FRAGMENT}
  ${F.FRESH_WATER_HOT_SENSOR_VALUES_FRAGMENT}
`;

export const THRUSTERS_MIMIC_QUERY = gql`
  query ThrustersMimic {
    ...ThrustersSensorValues
    ...ThrustersControlValues
    ...ThrustersParameters
    ...ThrustersControllerState
    ...PvtSensorValues
    ...PvtControlValues
    ...PvtParameters
    ...PcmSensorValues
  }
  ${F.THRUSTERS_SENSOR_VALUES_FRAGMENT}
  ${F.THRUSTERS_CONTROL_VALUES_FRAGMENT}
  ${F.THRUSTERS_PARAMETERS_FRAGMENT}
  ${F.THRUSTERS_CONTROLLER_STATE_FRAGMENT}
  ${F.PVT_SENSOR_VALUES_FRAGMENT}
  ${F.PVT_CONTROL_VALUES_FRAGMENT}
  ${F.PVT_PARAMETERS_FRAGMENT}
  ${F.PCM_SENSOR_VALUES_FRAGMENT}
`;

export const PVT_MIMIC_QUERY = gql`
  query PvtMimic {
    ...PvtSensorValues
    ...PvtControlValues
    ...PvtParameters
    ...PvtControllerState
    ...PcmSensorValues
  }
  ${F.PVT_SENSOR_VALUES_FRAGMENT}
  ${F.PVT_CONTROL_VALUES_FRAGMENT}
  ${F.PVT_PARAMETERS_FRAGMENT}
  ${F.PVT_CONTROLLER_STATE_FRAGMENT}
  ${F.PCM_SENSOR_VALUES_FRAGMENT}
`;

/** Shared by the pvt-main and pvt-owners mimics. */
export const PVT_SECTION_MIMIC_QUERY = gql`
  query PvtSectionMimic {
    ...PvtSensorValues
    ...PcmSensorValues
  }
  ${F.PVT_SENSOR_VALUES_FRAGMENT}
  ${F.PCM_SENSOR_VALUES_FRAGMENT}
`;

export const PCM_MIMIC_QUERY = gql`
  query PcmMimic {
    ...PcmSensorValues
    ...PcmControlValues
    ...PcmControllerState
    ...AdsorptionSensorValues
    ...ConsumersSensorValues
    ...ConsumersControlValues
    ...DhwSensorValues
    ...PvtSensorValues
    ...ThrustersSensorValues
    ...FreshWaterHotSensorValues
  }
  ${F.PCM_SENSOR_VALUES_FRAGMENT}
  ${F.PCM_CONTROL_VALUES_FRAGMENT}
  ${F.PCM_CONTROLLER_STATE_FRAGMENT}
  ${F.ADSORPTION_SENSOR_VALUES_FRAGMENT}
  ${F.CONSUMERS_SENSOR_VALUES_FRAGMENT}
  ${F.CONSUMERS_CONTROL_VALUES_FRAGMENT}
  ${F.DHW_SENSOR_VALUES_FRAGMENT}
  ${F.PVT_SENSOR_VALUES_FRAGMENT}
  ${F.THRUSTERS_SENSOR_VALUES_FRAGMENT}
  ${F.FRESH_WATER_HOT_SENSOR_VALUES_FRAGMENT}
`;

export const DC_MIMIC_QUERY = gql`
  query DcMimic {
    ...DcSensorValues
    ...DcControlValues
    ...DhwSensorValues
    ...DcAcConverterSensorValues
  }
  ${F.DC_SENSOR_VALUES_FRAGMENT}
  ${F.DC_CONTROL_VALUES_FRAGMENT}
  ${F.DHW_SENSOR_VALUES_FRAGMENT}
  ${F.DC_AC_CONVERTER_SENSOR_VALUES_FRAGMENT}
`;

/** Shared by the dc-aft, dc-ugrid and dc-fwd mimics, one per converter group. */
export const DC_SECTION_MIMIC_QUERY = gql`
  query DcSectionMimic {
    ...DcSensorValues
    ...DcControlValues
    ...DcAcConverterSensorValues
  }
  ${F.DC_SENSOR_VALUES_FRAGMENT}
  ${F.DC_CONTROL_VALUES_FRAGMENT}
  ${F.DC_AC_CONVERTER_SENSOR_VALUES_FRAGMENT}
`;

export const ADSORPTION_MIMIC_QUERY = gql`
  query AdsorptionMimic {
    ...AdsorptionSensorValues
    ...AdsorptionControlValues
    ...ConsumersSensorValues
    ...DhwSensorValues
    ...CoolingSensorValues
  }
  ${F.ADSORPTION_SENSOR_VALUES_FRAGMENT}
  ${F.ADSORPTION_CONTROL_VALUES_FRAGMENT}
  ${F.CONSUMERS_SENSOR_VALUES_FRAGMENT}
  ${F.DHW_SENSOR_VALUES_FRAGMENT}
  ${F.COOLING_SENSOR_VALUES_FRAGMENT}
`;

export const DRIVES_MIMIC_QUERY = gql`
  query DrivesMimic {
    ...DrivesSensorValues
    ...DrivesControlValues
    ...DcSensorValues
    ...DhwSensorValues
    ...PropulsionDriveSensorValues
    ...Dc700VShoreConverterSensorValues
  }
  ${F.DRIVES_SENSOR_VALUES_FRAGMENT}
  ${F.DRIVES_CONTROL_VALUES_FRAGMENT}
  ${F.DC_SENSOR_VALUES_FRAGMENT}
  ${F.DHW_SENSOR_VALUES_FRAGMENT}
  ${F.PROPULSION_DRIVE_SENSOR_VALUES_FRAGMENT}
  ${F.DC700_V_SHORE_CONVERTER_SENSOR_VALUES_FRAGMENT}
`;

export const DRIVES_SHOREPOWER_MIMIC_QUERY = gql`
  query DrivesShorepowerMimic {
    ...DrivesSensorValues
    ...Dc700VShoreConverterSensorValues
  }
  ${F.DRIVES_SENSOR_VALUES_FRAGMENT}
  ${F.DC700_V_SHORE_CONVERTER_SENSOR_VALUES_FRAGMENT}
`;

// Parameters pages

export const ADSORPTION_PARAMETERS_PAGE_QUERY = gql`
  query AdsorptionParametersPage {
    ...AdsorptionParameters
    ...AdsorptionControllerState
  }
  ${F.ADSORPTION_PARAMETERS_FRAGMENT}
  ${F.ADSORPTION_CONTROLLER_STATE_FRAGMENT}
`;

export const DHW_PARAMETERS_PAGE_QUERY = gql`
  query DhwParametersPage {
    ...DhwParameters
    ...DhwControllerState
  }
  ${F.DHW_PARAMETERS_FRAGMENT}
  ${F.DHW_CONTROLLER_STATE_FRAGMENT}
`;

export const THRUSTERS_PARAMETERS_PAGE_QUERY = gql`
  query ThrustersParametersPage {
    ...ThrustersParameters
    ...ThrustersControllerState
  }
  ${F.THRUSTERS_PARAMETERS_FRAGMENT}
  ${F.THRUSTERS_CONTROLLER_STATE_FRAGMENT}
`;

export const PVT_PARAMETERS_PAGE_QUERY = gql`
  query PvtParametersPage {
    ...PvtParameters
    ...PvtControllerState
  }
  ${F.PVT_PARAMETERS_FRAGMENT}
  ${F.PVT_CONTROLLER_STATE_FRAGMENT}
`;

export const PCM_PARAMETERS_PAGE_QUERY = gql`
  query PcmParametersPage {
    ...PcmParameters
    ...PcmControllerState
    ...ConsumersParameters
  }
  ${F.PCM_PARAMETERS_FRAGMENT}
  ${F.PCM_CONTROLLER_STATE_FRAGMENT}
  ${F.CONSUMERS_PARAMETERS_FRAGMENT}
`;

export const DC_PARAMETERS_PAGE_QUERY = gql`
  query DcParametersPage {
    ...DcParameters
    ...DcControllerState
  }
  ${F.DC_PARAMETERS_FRAGMENT}
  ${F.DC_CONTROLLER_STATE_FRAGMENT}
`;

export const DRIVES_PARAMETERS_PAGE_QUERY = gql`
  query DrivesParametersPage {
    ...DrivesParameters
    ...DrivesControllerState
  }
  ${F.DRIVES_PARAMETERS_FRAGMENT}
  ${F.DRIVES_CONTROLLER_STATE_FRAGMENT}
`;

// Simulator monitoring pages (sensor and control values of one module), for the modules thrsim's
// menu has.

export const MONITORING_PAGE_QUERIES: Record<ControlledModule, TypedDocumentNode> = {
  thrusters: gql`
    query ThrustersMonitoring {
      ...ThrustersSensorValues
      ...ThrustersControlValues
    }
    ${F.THRUSTERS_SENSOR_VALUES_FRAGMENT}
    ${F.THRUSTERS_CONTROL_VALUES_FRAGMENT}
  `,
  pcm: gql`
    query PcmMonitoring {
      ...PcmSensorValues
      ...PcmControlValues
    }
    ${F.PCM_SENSOR_VALUES_FRAGMENT}
    ${F.PCM_CONTROL_VALUES_FRAGMENT}
  `,
  pvt: gql`
    query PvtMonitoring {
      ...PvtSensorValues
      ...PvtControlValues
    }
    ${F.PVT_SENSOR_VALUES_FRAGMENT}
    ${F.PVT_CONTROL_VALUES_FRAGMENT}
  `,
  adsorption: gql`
    query AdsorptionMonitoring {
      ...AdsorptionSensorValues
      ...AdsorptionControlValues
    }
    ${F.ADSORPTION_SENSOR_VALUES_FRAGMENT}
    ${F.ADSORPTION_CONTROL_VALUES_FRAGMENT}
  `,
  consumers: gql`
    query ConsumersMonitoring {
      ...ConsumersSensorValues
      ...ConsumersControlValues
    }
    ${F.CONSUMERS_SENSOR_VALUES_FRAGMENT}
    ${F.CONSUMERS_CONTROL_VALUES_FRAGMENT}
  `,
  dc: gql`
    query DcMonitoring {
      ...DcSensorValues
      ...DcControlValues
    }
    ${F.DC_SENSOR_VALUES_FRAGMENT}
    ${F.DC_CONTROL_VALUES_FRAGMENT}
  `,
  dhw: gql`
    query DhwMonitoring {
      ...DhwSensorValues
      ...DhwControlValues
    }
    ${F.DHW_SENSOR_VALUES_FRAGMENT}
    ${F.DHW_CONTROL_VALUES_FRAGMENT}
  `,
  drives: gql`
    query DrivesMonitoring {
      ...DrivesSensorValues
      ...DrivesControlValues
    }
    ${F.DRIVES_SENSOR_VALUES_FRAGMENT}
    ${F.DRIVES_CONTROL_VALUES_FRAGMENT}
  `,
};

// Simulator controls pages (control values of one module)

export const CONTROLS_PAGE_QUERIES: Record<ControlledModule, TypedDocumentNode> = {
  thrusters: gql`
    query ThrustersControls {
      ...ThrustersControlValues
    }
    ${F.THRUSTERS_CONTROL_VALUES_FRAGMENT}
  `,
  pcm: gql`
    query PcmControls {
      ...PcmControlValues
    }
    ${F.PCM_CONTROL_VALUES_FRAGMENT}
  `,
  pvt: gql`
    query PvtControls {
      ...PvtControlValues
    }
    ${F.PVT_CONTROL_VALUES_FRAGMENT}
  `,
  adsorption: gql`
    query AdsorptionControls {
      ...AdsorptionControlValues
    }
    ${F.ADSORPTION_CONTROL_VALUES_FRAGMENT}
  `,
  consumers: gql`
    query ConsumersControls {
      ...ConsumersControlValues
    }
    ${F.CONSUMERS_CONTROL_VALUES_FRAGMENT}
  `,
  dc: gql`
    query DcControls {
      ...DcControlValues
    }
    ${F.DC_CONTROL_VALUES_FRAGMENT}
  `,
  dhw: gql`
    query DhwControls {
      ...DhwControlValues
    }
    ${F.DHW_CONTROL_VALUES_FRAGMENT}
  `,
  drives: gql`
    query DrivesControls {
      ...DrivesControlValues
    }
    ${F.DRIVES_CONTROL_VALUES_FRAGMENT}
  `,
};
