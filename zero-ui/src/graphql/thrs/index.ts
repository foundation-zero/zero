import { gql } from "@urql/vue";

export const sensorValues = (module: string) => gql`
  query ${module}SensorsValues {
  
  }
`;
