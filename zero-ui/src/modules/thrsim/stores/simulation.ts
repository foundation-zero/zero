import i18n from "@/i18n";
import { mqttGraphqlContext } from "@/modules/thrapp/graphql/client";
import { valueInputs } from "@/modules/thrapp/lib/mqtt-graphql.utils";
import { useThrsHistory } from "@/modules/thrapp/stores/history";

import { gql, TypedDocumentNode, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";

import { AmcsMode } from "@/modules/thrapp/types/thrs";
import { camelCase } from "lodash";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { SIMULATOR_QUERY } from "../lib/consts";
import { SIMULATION_TYPES, Simulator } from "../lib/consts.types";

// Requests a simulator status on the MQTT GraphQL API, which returns once the simulator has
// taken it; only a simulator in lockstep does.
export const SET_STATUS = gql`
  mutation ($input: ThrsControlSimulationStatusSetMessageInput!) {
    thrs {
      simulator {
        status(input: $input) {
          status
        }
      }
    }
  }
`;

// The simulator's inputs, as one input object; the response is not used.
const SIMULATION_INPUTS = gql`
  mutation ($input: ThrsControlThrsSimulationInputsInput!) {
    thrs {
      simulator {
        simulationInputs(input: $input) {
          __typename
        }
      }
    }
  }
`;

export const useSimulationStore = defineStore("simulation", () => {
  // For some reason the injected client does not come from the component in the outer scope.
  // This means we need to manually provide the context to each query and mutation.
  const { client } = useClientHandle();
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
        ?.value === AmcsMode.External,
  );

  // Sets some of the simulator's inputs, each field stamped, then reloads the simulator.
  const setInputs = async (input: Record<string, unknown>) => {
    const result = await client.mutation(SIMULATION_INPUTS, { input }, mqttGraphqlContext);
    if (!result.error) await refreshSimulation();
    return result;
  };

  const setAdvisory = async (enabled: boolean) => {
    if (!activeSimulationType.value || isProcessing.value) return;
    isProcessing.value = true;
    advisoryError.value = null;
    try {
      const mode = enabled ? AmcsMode.External : AmcsMode.Manual;
      const result = await setInputs({ mode: valueInputs({ mode }) });
      if (result.error) {
        advisoryError.value = result.error.message ?? i18n.global.t("thrs.labels.failedToSubmit");
        return;
      }
      await useThrsHistory().refresh();
    } catch (err) {
      advisoryError.value =
        err instanceof Error ? err.message : i18n.global.t("thrs.labels.failedToSubmit");
    } finally {
      isProcessing.value = false;
    }
  };

  // Sends one of the simulator's directives, then reloads the simulator.
  const send = async (query: TypedDocumentNode, variables: Record<string, unknown> = {}) => {
    if (isProcessing.value) return;

    isProcessing.value = true;
    let result: Maybe<OperationResult> = undefined;

    try {
      result = await client.mutation(query, variables, mqttGraphqlContext);
      await refreshSimulation();
    } catch (error) {
      console.error("Error executing mutation:", error);
    } finally {
      isProcessing.value = false;
    }

    return result;
  };

  const play = (playbackRate: number) =>
    send(SET_STATUS, { input: { status: "RUNNING", playbackRate, pauseAt: null } });

  const pause = () => send(SET_STATUS, { input: { status: "AVAILABLE", pauseAt: null } });

  // Steps as fast as possible until `seconds` after the simulation time. Only a paused
  // simulator steps, and its time stands still, so the last polled one is current.
  const step = (seconds: number) => {
    const simulationTime = status.value?.simulationTime;
    if (!simulationTime) return;
    const pauseAt = new Date(new Date(simulationTime).getTime() + seconds * 1000).toISOString();
    return send(SET_STATUS, { input: { status: "STEPPING", pauseAt } });
  };

  return {
    simulation,
    refreshSimulation,
    startPolling,
    stopPolling,
    pause,
    play,
    step,
    setInputs,
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
