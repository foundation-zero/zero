import i18n from "@/i18n";
import { PromiseFn } from "@/modules/common/types";
import { mutationWithoutValue, mutationWithValue } from "@/modules/thrapp/graphql";
import { context, mqttGraphqlContext } from "@/modules/thrapp/graphql/client";
import { useThrsHistory } from "@/modules/thrapp/stores/history";

import { TypedDocumentNode, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";

import { AmcsControlMode } from "@/modules/thrapp/types/thrs";
import { camelCase } from "lodash";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { SIMULATION_INPUT_QUERIES, SIMULATOR_QUERY } from "../lib/consts";
import { SIMULATION_TYPES, Simulator } from "../lib/consts.types";

export const useSimulationStore = defineStore("simulation", () => {
  // For some reason the injected client does not come from the component in the outer scope.
  // This means we need to manually provide the context to each query and mutation.
  const { client } = useClientHandle();
  const pause = mutationWithoutValue("simulationPause");
  const play = mutationWithValue("simulationPlay", "playbackRate", "Float");
  const step = mutationWithValue("simulationStep", "seconds", "Float!");
  // TODO: make set automated control module dependent
  const isProcessing = ref(false);
  const simulatorQuery = useQuery<Simulator>({
    query: SIMULATOR_QUERY,
    context: mqttGraphqlContext,
    requestPolicy: "network-only",
  });
  const simulator = computed(() => simulatorQuery.data.value?.thrs?.simulator);
  const refreshSimulation = () => simulatorQuery.executeQuery({ requestPolicy: "network-only" });

  const status = computed(() => simulator.value?.status ?? undefined);
  // Without a status, as from a simulator that runs apart from the controller, there is no
  // simulation to show.
  const simulation = computed(() =>
    status.value
      ? {
          inputs: simulator.value?.simulationInputs ?? undefined,
          outputs: simulator.value?.simulationOutputs ?? undefined,
        }
      : undefined,
  );
  const activeSimulationType = computed(() =>
    SIMULATION_TYPES.find((type) => type === camelCase(status.value?.mode)),
  );

  // Poll only while a simulation view is open; the store outlives the views.
  const { resume: startPolling, pause: stopPolling } = useIntervalFn(refreshSimulation, 5000, {
    immediate: false,
    immediateCallback: true,
  });

  const isAvailable = computed(() => status.value?.status === "AVAILABLE");
  const isRunning = computed(() => status.value?.status === "RUNNING");
  const isStepping = computed(() => status.value?.status === "STEPPING");

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
      const result = await client.mutation(query, { input }, context);
      if (result.error) {
        advisoryError.value = result.error.message ?? i18n.global.t("thrs.labels.failedToSubmit");
        return;
      }
      await useThrsHistory().refresh();
      await refreshSimulation();
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
    startPolling,
    stopPolling,
    pause: mutationFn(pause, refreshSimulation),
    play: mutationFn<number>(play, refreshSimulation),
    step: mutationFn<number>(step, refreshSimulation),
    setAdvisory,
    isAdvisory,
    advisoryError,
    status,
    isAvailable,
    isRunning,
    isProcessing,
    isStepping,
    activeSimulationType,
  };
});
