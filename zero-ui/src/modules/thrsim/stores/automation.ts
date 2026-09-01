import { PromiseFn } from "@/modules/domestic/types";
import { mutationWithValue } from "@/modules/thrsim/graphql";
import { context } from "@/modules/thrsim/graphql/client";

import { Nullable } from "@/modules/loads/types";
import { gql, TypedDocumentNode, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";

import { defineStore } from "pinia";
import { ref } from "vue";
import { AmcsControlModeSensor, PvtMode } from "../types";

export type ThrustersAutomaticMode = { mode: string };
export type PcmAutomaticMode = { mode: string };
export type PvtAutomaticMode = {
  aft: { mode: PvtMode };
  fwd: { mode: PvtMode };
  owners: { mode: PvtMode };
};
export type AdsorptionAutomaticMode = { mode: string };
export type ConsumersAutomaticMode = Record<string, never>;
export type ConvertersAutomaticMode = { mode: string };
export type DcAutomaticMode = {
  brightloopsAft: ConvertersAutomaticMode;
  brightloopsFwd: ConvertersAutomaticMode;
  ugrids: ConvertersAutomaticMode;
};
export type DhwAutomaticMode = { boostingMode: string; fillingMode: string };
export type DrivesAutomaticMode = { mode: string };

export type AutomaticMode =
  | ThrustersAutomaticMode
  | PcmAutomaticMode
  | PvtAutomaticMode
  | AdsorptionAutomaticMode
  | ConsumersAutomaticMode
  | DcAutomaticMode
  | DhwAutomaticMode
  | DrivesAutomaticMode;

export type ControlMode<T extends AutomaticMode = AutomaticMode> = {
  automatic: boolean;
  automaticMode: Nullable<T>;
};

export type ControlModes = {
  thrusters: ThrustersAutomaticMode;
  pcm: PcmAutomaticMode;
  pvt: PvtAutomaticMode;
  adsorption: AdsorptionAutomaticMode;
  consumers: ConsumersAutomaticMode;
  dc: DcAutomaticMode;
  dhw: DhwAutomaticMode;
  drives: DrivesAutomaticMode;
};

export type ControlStatus = {
  modules: {
    [K in keyof ControlModes]: {
      controlMode: ControlMode<ControlModes[K]>;
      sensorValues: Record<`mode`, AmcsControlModeSensor>;
    };
  };
};

export const CONTROL_QUERY = gql`
  query ControlStatus {
    modules {
      thrusters {
        controlMode {
          automatic
          automaticMode {
            mode
          }
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
      pvt {
        controlMode {
          automatic
          automaticMode {
            aft {
              mode
            }
            fwd {
              mode
            }
            owners {
              mode
            }
          }
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
      pcm {
        controlMode {
          automatic
          automaticMode {
            mode
          }
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
      adsorption {
        controlMode {
          automatic
          automaticMode {
            mode
          }
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
      consumers {
        controlMode {
          automatic
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
      dc {
        controlMode {
          automatic
          automaticMode {
            brightloopsAft {
              mode
            }
            brightloopsFwd {
              mode
            }
            ugrids {
              mode
            }
          }
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
      dhw {
        controlMode {
          automatic
          automaticMode {
            boostingMode
            fillingMode
          }
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
      drives {
        controlMode {
          automatic
          automaticMode {
            mode
          }
        }
        sensorValues {
          mode {
            mode {
              value
            }
          }
        }
      }
    }
  }
`;

export const useAutomationStore = defineStore("automation", () => {
  // For some reason the injected client does not come from the component in the outer scope.
  // This means we need to manually provide the context to each query and mutation.
  const { client } = useClientHandle();
  // TODO: make set automated control module dependent (as an arg instead of a separate mutation)
  const setAutomatedControl = (module: string) =>
    mutationWithValue(`${module}SetAutomationMode`, "automatic", "Boolean!");
  const isProcessing = ref(false);

  const controlQuery = useQuery<ControlStatus>({
    query: CONTROL_QUERY,
    context,
  });

  // Use network-only policy to always get the latest control mode
  const updateControl = () => controlQuery.executeQuery({ requestPolicy: "network-only" });

  useIntervalFn(updateControl, 5000, {
    immediate: true,
  });

  type MutationFnParams = [query: TypedDocumentNode, onSuccess: PromiseFn];

  function mutationFn(...args: MutationFnParams): () => Promise<Maybe<OperationResult>>;
  function mutationFn<T>(...args: MutationFnParams): (value: T) => Promise<Maybe<OperationResult>>;
  function mutationFn<T>(...[query, onSuccess]: MutationFnParams) {
    return async (value?: T) => {
      if (isProcessing.value) return;

      isProcessing.value = true;
      let result: Maybe<OperationResult> = undefined;

      try {
        result = await client.mutation(query, value === undefined ? {} : { value }, context);
        await onSuccess();
      } catch (error) {
        console.error("Error executing mutation:", error);
      } finally {
        isProcessing.value = false;
      }

      return result;
    };
  }

  return {
    setAutomatedControl: (module: string) =>
      mutationFn<boolean>(setAutomatedControl(module), updateControl),
    control: controlQuery.data,
    isProcessing,
  };
});
