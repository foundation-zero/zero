import { PromiseFn } from "@/modules/domestic/types";
import { mutationWithValue } from "@/modules/thrs/graphql";
import { context } from "@/modules/thrs/graphql/client";

import { Nullable } from "@/modules/loads/types";
import { gql, TypedDocumentNode, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";

import { defineStore } from "pinia";
import { ref } from "vue";

export type ThrustersAutomaticMode = { mode: string };
export type PcmAutomaticMode = { mode: string };
export type PvtAutomaticMode = {
  aft: { mode: string };
  fwd: { mode: string };
  owners: { mode: string };
};
export type DhwAutomaticMode = { boostingMode: string; fillingMode: string };
export type ConsumersAutomaticMode = Record<string, never>;

export type AutomaticMode =
  | ThrustersAutomaticMode
  | PcmAutomaticMode
  | PvtAutomaticMode
  | DhwAutomaticMode
  | ConsumersAutomaticMode;

export type ControlMode<T extends AutomaticMode = AutomaticMode> = {
  automatic: boolean;
  automaticMode: Nullable<T>;
};

export type ControlModes = {
  thrusters: ThrustersAutomaticMode;
  pcm: PcmAutomaticMode;
  pvt: PvtAutomaticMode;
  dhw: DhwAutomaticMode;
  consumers: ConsumersAutomaticMode;
};

export type ControlStatus = {
  modules: {
    [K in keyof ControlModes]: {
      controlMode: ControlMode<ControlModes[K]>;
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
      }
      pcm {
        controlMode {
          automatic
          automaticMode {
            mode
          }
        }
      }
      consumers {
        controlMode {
          automatic
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
      }
    }
  }
`;

export const useAutomationStore = defineStore("automation", () => {
  // For some reason the injected client does not come from the component in the outer scope.
  // This means we need to manually provide the context to each query and mutation.
  const { client } = useClientHandle();
  // TODO: make set automated control module dependent
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
