import { PromiseFn } from "@/modules/domestic/types";
import { mutationWithoutValue, mutationWithValue } from "@/modules/thrs/graphql";
import { context } from "@/modules/thrs/graphql/client";

import { Nullable } from "@/modules/loads/types";
import { gql, TypedDocumentNode, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";

import { defineStore } from "pinia";
import { computed, ref, toRefs } from "vue";
import { SIMULATION_TYPES } from "../lib/consts.types";
import { useThrsHistory } from "./history";

export type SimulationStatus = {
  simulation: {
    status: "running" | "available" | "stepping";
    time: number;
  };
};

export type ThrustersAutomaticMode = { mode: string };
export type PcmAutomaticMode = { mode: string };
export type PvtAutomaticMode = {
  aft: { mode: string };
  fwd: { mode: string };
  owners: { mode: string };
};
export type BoilersAutomaticMode = { boostingMode: string; fillingMode: string };
export type ConsumersAutomaticMode = Record<string, never>;

export type AutomaticMode =
  | ThrustersAutomaticMode
  | PcmAutomaticMode
  | PvtAutomaticMode
  | BoilersAutomaticMode
  | ConsumersAutomaticMode;

export type ControlMode = {
  automatic: boolean;
  automaticMode: Nullable<AutomaticMode>;
};

export type ControlStatus = {
  modules: Record<
    string,
    {
      controlMode: Nullable<ControlMode>;
    }
  >;
};

export const STATUS_QUERY = gql`
  query SimulationStatus {
    simulation {
      status
      time
    }
  }
`;

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
      boilers {
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

export const useSimulationStore = defineStore("simulation", () => {
  // For some reason the injected client does not come from the component in the outer scope.
  // This means we need to manually provide the context to each query and mutation.
  const { client } = useClientHandle();
  const pause = mutationWithoutValue("simulationPause");
  const play = mutationWithValue("simulationPlay", "playbackRate", "Float");
  const step = mutationWithValue("simulationStep", "seconds", "Float!");
  // TODO: make set automated control module dependent
  const setAutomatedControl = (module: string) =>
    mutationWithValue(`${module}SetAutomationMode`, "automatic", "Boolean!");
  const isProcessing = ref(false);
  const { data } = toRefs(useThrsHistory());
  const activeSimulation = computed(() => data.value?.simulation.inputs?.__typename);
  const activeSimulationType = computed(() =>
    SIMULATION_TYPES.find((type) => activeSimulation.value?.toLocaleLowerCase().startsWith(type)),
  );

  const statusQuery = useQuery<SimulationStatus>({
    query: STATUS_QUERY,
    context,
  });

  const controlQuery = useQuery<ControlStatus>({
    query: CONTROL_QUERY,
    context,
  });

  // Use network-only policy to always get the latest status
  const updateStatus = () => statusQuery.executeQuery({ requestPolicy: "network-only" });
  const updateControl = () => controlQuery.executeQuery({ requestPolicy: "network-only" });

  useIntervalFn(updateStatus, 5000, {
    immediate: true,
  });

  useIntervalFn(updateControl, 5000, {
    immediate: true,
  });

  const status = computed(() => statusQuery.data?.value?.simulation.status);
  const isAvailable = computed(() => status.value === "available");
  const isRunning = computed(() => status.value === "running");
  const isStepping = computed(() => status.value === "stepping");

  type MutationFnParams = [query: TypedDocumentNode, onSuccess: PromiseFn];

  function mutationFn(...args: MutationFnParams): () => Promise<Maybe<OperationResult>>;
  function mutationFn<T>(...args: MutationFnParams): (value: T) => Promise<Maybe<OperationResult>>;
  function mutationFn<T>(...[query, onSuccess]: MutationFnParams) {
    return async (value?: T) => {
      if (isProcessing.value) return;

      isProcessing.value = true;
      let result: Maybe<OperationResult>;

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
    pause: mutationFn(pause, updateStatus),
    play: mutationFn<number>(play, updateStatus),
    step: mutationFn<number>(step, updateStatus),
    setAutomatedControl: (module: string) =>
      mutationFn<boolean>(setAutomatedControl(module), updateControl),
    status: statusQuery.data,
    control: controlQuery.data,
    isAvailable,
    isRunning,
    isProcessing,
    isStepping,
    activeSimulation,
    activeSimulationType,
  };
});
