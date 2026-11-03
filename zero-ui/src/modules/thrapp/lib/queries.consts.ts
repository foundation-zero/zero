import { gql, TypedDocumentNode } from "@urql/vue";
import { ThrsModules } from "./consts.types";
import * as Queries from "./queries.generated";

// Queries per view, holding only the modules and module parts that the view shows.

// Mimics

export const DHW_MIMIC_QUERY = gql`
  query DhwMimic {
    modules {
      dhw {
        sensorValues {
          ${Queries.DHW_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DHW_CONTROL_QUERY}
        }
        parameters {
          ${Queries.DHW_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.DHW_CONTROLLER_STATE_QUERY}
        }
      }
      adsorption {
        sensorValues {
          ${Queries.ADSORPTION_SENSOR_QUERY}
        }
      }
      consumers {
        sensorValues {
          ${Queries.CONSUMERS_SENSOR_QUERY}
        }
      }
      dc {
        sensorValues {
          ${Queries.DC_SENSOR_QUERY}
        }
      }
      drives {
        sensorValues {
          ${Queries.DRIVES_SENSOR_QUERY}
        }
      }
    }
  }
`;

export const THRUSTERS_MIMIC_QUERY = gql`
  query ThrustersMimic {
    modules {
      thrusters {
        sensorValues {
          ${Queries.THRUSTERS_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.THRUSTERS_CONTROL_QUERY}
        }
        parameters {
          ${Queries.THRUSTERS_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.THRUSTERS_CONTROLLER_STATE_QUERY}
        }
      }
      pvt {
        sensorValues {
          ${Queries.PVT_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.PVT_CONTROL_QUERY}
        }
        parameters {
          ${Queries.PVT_PARAMETERS_QUERY}
        }
      }
    }
  }
`;

export const PVT_MIMIC_QUERY = gql`
  query PvtMimic {
    modules {
      pvt {
        sensorValues {
          ${Queries.PVT_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.PVT_CONTROL_QUERY}
        }
        parameters {
          ${Queries.PVT_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.PVT_CONTROLLER_STATE_QUERY}
        }
      }
    }
  }
`;

/** Shared by the pvt-main, pvt-owners and pvt-main-heat mimics. */
export const PVT_SECTION_MIMIC_QUERY = gql`
  query PvtSectionMimic {
    modules {
      pvt {
        sensorValues {
          ${Queries.PVT_SENSOR_QUERY}
        }
      }
    }
  }
`;

export const PCM_MIMIC_QUERY = gql`
  query PcmMimic {
    modules {
      pcm {
        sensorValues {
          ${Queries.PCM_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.PCM_CONTROL_QUERY}
        }
        controllerState {
          ${Queries.PCM_CONTROLLER_STATE_QUERY}
        }
      }
      adsorption {
        sensorValues {
          ${Queries.ADSORPTION_SENSOR_QUERY}
        }
      }
      consumers {
        sensorValues {
          ${Queries.CONSUMERS_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.CONSUMERS_CONTROL_QUERY}
        }
      }
      dhw {
        sensorValues {
          ${Queries.DHW_SENSOR_QUERY}
        }
      }
      pvt {
        sensorValues {
          ${Queries.PVT_SENSOR_QUERY}
        }
      }
      thrusters {
        sensorValues {
          ${Queries.THRUSTERS_SENSOR_QUERY}
        }
      }
    }
  }
`;

export const DC_MIMIC_QUERY = gql`
  query DcMimic {
    modules {
      dc {
        sensorValues {
          ${Queries.DC_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DC_CONTROL_QUERY}
        }
      }
      dhw {
        sensorValues {
          ${Queries.DHW_SENSOR_QUERY}
        }
      }
    }
  }
`;

export const DRIVES_MIMIC_QUERY = gql`
  query DrivesMimic {
    modules {
      drives {
        sensorValues {
          ${Queries.DRIVES_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DRIVES_CONTROL_QUERY}
        }
      }
      dc {
        sensorValues {
          ${Queries.DC_SENSOR_QUERY}
        }
      }
      dhw {
        sensorValues {
          ${Queries.DHW_SENSOR_QUERY}
        }
      }
    }
  }
`;

// Parameters pages

export const ADSORPTION_PARAMETERS_PAGE_QUERY = gql`
  query AdsorptionParameters {
    modules {
      adsorption {
        parameters {
          ${Queries.ADSORPTION_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.ADSORPTION_CONTROLLER_STATE_QUERY}
        }
      }
    }
  }
`;

export const DHW_PARAMETERS_PAGE_QUERY = gql`
  query DhwParameters {
    modules {
      dhw {
        parameters {
          ${Queries.DHW_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.DHW_CONTROLLER_STATE_QUERY}
        }
      }
    }
  }
`;

export const THRUSTERS_PARAMETERS_PAGE_QUERY = gql`
  query ThrustersParameters {
    modules {
      thrusters {
        parameters {
          ${Queries.THRUSTERS_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.THRUSTERS_CONTROLLER_STATE_QUERY}
        }
      }
    }
  }
`;

export const PVT_PARAMETERS_PAGE_QUERY = gql`
  query PvtParameters {
    modules {
      pvt {
        parameters {
          ${Queries.PVT_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.PVT_CONTROLLER_STATE_QUERY}
        }
      }
    }
  }
`;

export const PCM_PARAMETERS_PAGE_QUERY = gql`
  query PcmParameters {
    modules {
      pcm {
        parameters {
          ${Queries.PCM_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.PCM_CONTROLLER_STATE_QUERY}
        }
      }
      consumers {
        parameters {
          ${Queries.CONSUMERS_PARAMETERS_QUERY}
        }
      }
    }
  }
`;

export const DC_PARAMETERS_PAGE_QUERY = gql`
  query DcParameters {
    modules {
      dc {
        parameters {
          ${Queries.DC_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.DC_CONTROLLER_STATE_QUERY}
        }
      }
    }
  }
`;

export const DRIVES_PARAMETERS_PAGE_QUERY = gql`
  query DrivesParameters {
    modules {
      drives {
        parameters {
          ${Queries.DRIVES_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.DRIVES_CONTROLLER_STATE_QUERY}
        }
      }
    }
  }
`;

// Simulator monitoring pages (sensor and control values of one module)

export const THRUSTERS_MONITORING_PAGE_QUERY = gql`
  query ThrustersMonitoring {
    modules {
      thrusters {
        sensorValues {
          ${Queries.THRUSTERS_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.THRUSTERS_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const PCM_MONITORING_PAGE_QUERY = gql`
  query PcmMonitoring {
    modules {
      pcm {
        sensorValues {
          ${Queries.PCM_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.PCM_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const PVT_MONITORING_PAGE_QUERY = gql`
  query PvtMonitoring {
    modules {
      pvt {
        sensorValues {
          ${Queries.PVT_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.PVT_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const ADSORPTION_MONITORING_PAGE_QUERY = gql`
  query AdsorptionMonitoring {
    modules {
      adsorption {
        sensorValues {
          ${Queries.ADSORPTION_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.ADSORPTION_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const CONSUMERS_MONITORING_PAGE_QUERY = gql`
  query ConsumersMonitoring {
    modules {
      consumers {
        sensorValues {
          ${Queries.CONSUMERS_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.CONSUMERS_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const DC_MONITORING_PAGE_QUERY = gql`
  query DcMonitoring {
    modules {
      dc {
        sensorValues {
          ${Queries.DC_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DC_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const DHW_MONITORING_PAGE_QUERY = gql`
  query DhwMonitoring {
    modules {
      dhw {
        sensorValues {
          ${Queries.DHW_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DHW_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const DRIVES_MONITORING_PAGE_QUERY = gql`
  query DrivesMonitoring {
    modules {
      drives {
        sensorValues {
          ${Queries.DRIVES_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DRIVES_CONTROL_QUERY}
        }
      }
    }
  }
`;

// Simulator controls pages (control values of one module)

export const THRUSTERS_CONTROLS_PAGE_QUERY = gql`
  query ThrustersControls {
    modules {
      thrusters {
        controlValues {
          ${Queries.THRUSTERS_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const PCM_CONTROLS_PAGE_QUERY = gql`
  query PcmControls {
    modules {
      pcm {
        controlValues {
          ${Queries.PCM_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const PVT_CONTROLS_PAGE_QUERY = gql`
  query PvtControls {
    modules {
      pvt {
        controlValues {
          ${Queries.PVT_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const ADSORPTION_CONTROLS_PAGE_QUERY = gql`
  query AdsorptionControls {
    modules {
      adsorption {
        controlValues {
          ${Queries.ADSORPTION_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const CONSUMERS_CONTROLS_PAGE_QUERY = gql`
  query ConsumersControls {
    modules {
      consumers {
        controlValues {
          ${Queries.CONSUMERS_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const DC_CONTROLS_PAGE_QUERY = gql`
  query DcControls {
    modules {
      dc {
        controlValues {
          ${Queries.DC_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const DHW_CONTROLS_PAGE_QUERY = gql`
  query DhwControls {
    modules {
      dhw {
        controlValues {
          ${Queries.DHW_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const DRIVES_CONTROLS_PAGE_QUERY = gql`
  query DrivesControls {
    modules {
      drives {
        controlValues {
          ${Queries.DRIVES_CONTROL_QUERY}
        }
      }
    }
  }
`;

export const MONITORING_PAGE_QUERIES: Record<keyof ThrsModules, TypedDocumentNode> = {
  thrusters: THRUSTERS_MONITORING_PAGE_QUERY,
  pcm: PCM_MONITORING_PAGE_QUERY,
  pvt: PVT_MONITORING_PAGE_QUERY,
  adsorption: ADSORPTION_MONITORING_PAGE_QUERY,
  consumers: CONSUMERS_MONITORING_PAGE_QUERY,
  dc: DC_MONITORING_PAGE_QUERY,
  dhw: DHW_MONITORING_PAGE_QUERY,
  drives: DRIVES_MONITORING_PAGE_QUERY,
};

export const CONTROLS_PAGE_QUERIES: Record<keyof ThrsModules, TypedDocumentNode> = {
  thrusters: THRUSTERS_CONTROLS_PAGE_QUERY,
  pcm: PCM_CONTROLS_PAGE_QUERY,
  pvt: PVT_CONTROLS_PAGE_QUERY,
  adsorption: ADSORPTION_CONTROLS_PAGE_QUERY,
  consumers: CONSUMERS_CONTROLS_PAGE_QUERY,
  dc: DC_CONTROLS_PAGE_QUERY,
  dhw: DHW_CONTROLS_PAGE_QUERY,
  drives: DRIVES_CONTROLS_PAGE_QUERY,
};
