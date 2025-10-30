import { PromiseFn } from "@/@types";
import { mutationWithoutValue, mutationWithValue } from "@/graphql/thrs";
import { context } from "@/graphql/thrs/client";

import { gql, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";
import { TypedDocumentNode } from "msw/core/graphql";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

type SimulationStatus = {
  simulation: {
    status: "running" | "available" | "stepping";
    time: number;
  };
};

type ControlStatus = {
  control: {
    automatic: boolean;
  };
};

const STATUS_QUERY = gql`
  query SimulationStatus {
    simulation {
      status
      time
    }
  }
`;

const CONTROL_QUERY = gql`
  query SimulationStatus {
    control {
      automatic
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
  const setAutomatedControl = mutationWithValue(
    "controlSetAutomationMode",
    "automatic",
    "Boolean!",
  );
  const isProcessing = ref(false);

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
    setAutomatedControl: mutationFn<boolean>(setAutomatedControl, updateControl),
    status: statusQuery.data,
    control: controlQuery.data,
    isAvailable,
    isRunning,
    isProcessing,
    isStepping,
  };
});
