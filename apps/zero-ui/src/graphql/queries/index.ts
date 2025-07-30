import { gql } from "@urql/vue";

export const ControlsLogItem = gql`
  fragment ControlsLogItem on ControlsLog {
    id
    value
    time
  }
`;

export const SensorsLogItem = gql`
  fragment SensorsLogItem on SensorsLog {
    id
    value
    time
  }
`;

export const mutationResponse = gql`
  fragment MutationResponse on MutationResponse {
    code
    success
    message
  }
`;
