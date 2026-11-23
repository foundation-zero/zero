import { gql } from "@urql/vue";

export const MONITORING_SERIES = gql`
  query MonitoringSeries(
    $module: MonitoringModule!
    $metrics: [MonitoringMetric!]!
    $start: DateTime!
    $end: DateTime!
    $devices: [String!]
  ) {
    monitoringSeries(
      module: $module
      metrics: $metrics
      start: $start
      end: $end
      devices: $devices
    ) {
      metric
      unit
      step
      binSeconds
      devices {
        device
        yardTag
        times
        values
        latest {
          value
          timestamp
        }
      }
    }
  }
`;

export const MONITORING_STATES = gql`
  query MonitoringStates(
    $module: MonitoringModule!
    $signals: [MonitoringSignal!]!
    $start: DateTime!
    $end: DateTime!
  ) {
    monitoringStates(module: $module, signals: $signals, start: $start, end: $end) {
      signal
      segments {
        state
        start
        end
      }
    }
  }
`;

const ANNOTATION_FIELDS = `
  id
  kind
  time
  text
  author
  canDelete
  changes {
    name
    previous
    value
  }
`;

export const MONITORING_ANNOTATIONS = gql`
  query MonitoringAnnotations(
    $module: MonitoringModule!
    $start: DateTime!
    $end: DateTime!
    $ownerKey: String
  ) {
    monitoringAnnotations(module: $module, start: $start, end: $end, ownerKey: $ownerKey) {
      ${ANNOTATION_FIELDS}
    }
  }
`;

export const ADD_MONITORING_ANNOTATION = gql`
  mutation AddMonitoringAnnotation(
    $module: MonitoringModule!
    $time: DateTime!
    $text: String!
    $author: String
    $ownerKey: String!
  ) {
    addMonitoringAnnotation(
      module: $module
      time: $time
      text: $text
      author: $author
      ownerKey: $ownerKey
    ) {
      ${ANNOTATION_FIELDS}
    }
  }
`;

export const DELETE_MONITORING_ANNOTATION = gql`
  mutation DeleteMonitoringAnnotation($id: ID!, $time: DateTime!, $ownerKey: String!) {
    deleteMonitoringAnnotation(id: $id, time: $time, ownerKey: $ownerKey)
  }
`;
