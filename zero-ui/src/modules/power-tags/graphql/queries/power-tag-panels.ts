import { gql } from "@urql/vue";

export const POWER_TAG_PANELS = gql`
  query GetPowerTagPanels {
    powerTagPanels: powerTagBuckets {
      id
      powerTags {
        topic
        metadata {
          panel
          slug
          component
          consumer
          values {
            name
            unit
          }
        }
        values {
          currentA
          currentB
          currentC
          currentN
          voltageAn
          voltageBn
          voltageCn
          activePowerA
          activePowerB
          activePowerC
          activePowerTotal
          powerFactorA
          powerFactorB
          powerFactorC
          powerFactorTotal
        }
      }
    }
  }
`;
