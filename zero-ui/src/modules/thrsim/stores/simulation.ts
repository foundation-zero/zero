import i18n from "@/i18n";
import { PromiseFn } from "@/modules/common/types";
import { mutationWithoutValue, mutationWithValue } from "@/modules/thrapp/graphql";
import { context } from "@/modules/thrapp/graphql/client";
import { useThrsHistory } from "@/modules/thrapp/stores/history";

import { gql, TypedDocumentNode, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";

import { AmcsControlMode } from "@/modules/thrapp/types/thrs";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { QUERY_SIMULATION, SIMULATION_INPUT_QUERIES, THRSIM } from "../lib/consts";
import { SIMULATION_TYPES } from "../lib/consts.types";

export type SimulationStatus = {
  simulation: {
    status: "running" | "available" | "stepping";
    time: number;
  };
};

export const STATUS_QUERY = gql`
  query SimulationStatus {
    simulation {
      status
      time
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
  const isProcessing = ref(false);
  const simulationQuery = useQuery<THRSIM>({
    query: QUERY_SIMULATION,
    context,
    requestPolicy: "network-only",
  });
  const simulation = computed(() => simulationQuery.data.value?.simulation);
  const refreshSimulation = () => simulationQuery.executeQuery({ requestPolicy: "network-only" });

  useIntervalFn(refreshSimulation, 5000, { immediate: true });

  const activeSimulation = computed(() => simulation.value?.inputs?.__typename);
  const activeSimulationType = computed(() =>
    SIMULATION_TYPES.find((type) =>
      `${activeSimulation.value?.charAt(0)?.toLowerCase()}${activeSimulation.value?.slice(1)}`.startsWith(
        type,
      ),
    ),
  );

  const statusQuery = useQuery<SimulationStatus>({
    query: STATUS_QUERY,
    context,
  });

  // Use network-only policy to always get the latest status
  const updateStatus = () => statusQuery.executeQuery({ requestPolicy: "network-only" });

  useIntervalFn(updateStatus, 5000, {
    immediate: true,
  });

  const status = computed(() => statusQuery.data?.value?.simulation.status);
  const isAvailable = computed(() => status.value === "available");
  const isRunning = computed(() => status.value === "running");
  const isStepping = computed(() => status.value === "stepping");

  const advisoryError = ref<string | null>(null);
  const isAdvisory = computed(
    () =>
      (simulation.value?.inputs as { mode?: { mode?: { value?: string } } } | undefined)?.mode?.mode
        ?.value === AmcsControlMode.External,
  );

  const setAdvisory = async (enabled: boolean) => {
    const type = activeSimulationType.value;
    if (!type || isProcessing.value) return;
    isProcessing.value = true;
    advisoryError.value = null;
    try {
      const mutation = `${type}SimulationSetMode`;
      const query = `mutation ($input: AmcsControlModeInputType!) {
      ${mutation}(value: $input) {
        ${SIMULATION_INPUT_QUERIES[type]}
      }
    }`;
      const input = { mode: enabled ? AmcsControlMode.External : AmcsControlMode.Manual };
      const history = useThrsHistory();
      const result = await history.mutate(query, { input });
      const resultError = (result as { error?: { message?: string } })?.error;
      if (resultError) {
        advisoryError.value = resultError.message ?? i18n.global.t("thrs.labels.failedToSubmit");
        return;
      }
      await history.refresh();
      await refreshSimulation();
      await updateStatus();
    } catch (err) {
      advisoryError.value =
        err instanceof Error ? err.message : i18n.global.t("thrs.labels.failedToSubmit");
    } finally {
      isProcessing.value = false;
    }
  };

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
    simulation,
    refreshSimulation,
    pause: mutationFn(pause, updateStatus),
    play: mutationFn<number>(play, updateStatus),
    step: mutationFn<number>(step, updateStatus),
    setAdvisory,
    isAdvisory,
    advisoryError,
    status: statusQuery.data,
    isAvailable,
    isRunning,
    isProcessing,
    isStepping,
    activeSimulation,
    activeSimulationType,
  };
});
