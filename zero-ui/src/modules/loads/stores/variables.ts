import { useQuery } from "@urql/vue";
import { useIntervalFn, useLocalStorage } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed } from "vue";
import { LOADS_CONTEXT } from "../graphql/client";
import {
  VARIABLE_ACTUALS,
  VARIABLE_DEFINITIONS,
  VARIABLE_REFERENCE_VALUES,
} from "../graphql/queries/variables";
import { AWA_VALUES, AWS_VALUES } from "../lib/consts";
import { Dashboard, DASHBOARDS, OVERVIEW } from "../lib/consts.dashboards";
import { SailId, SAILS } from "../lib/consts.sails";
import { AWA, MaybeVariable, NumRangeId, Sail, Variable } from "../types";
import {
  QueryVariableActual,
  QueryVariableDefinition,
  QueryVariableReference,
} from "../types/queries";

const UPDATE_INTERVAL_MS = 5000;

export const useVariablesStore = defineStore("loads-variables", () => {
  const selectedAWA = useLocalStorage<AWA>("loads-variable-awa", AWA_VALUES[0].id);
  const selectedAWS = useLocalStorage<NumRangeId>("loads-variable-aws", AWS_VALUES[0].id);

  const selectedDashboardId = useLocalStorage<SailId>(
    "loads-variable-selected-dashboard",
    SailId.None,
  );
  const selectedDashboard = computed<Dashboard>({
    get() {
      return DASHBOARDS.find((d) => d.sail === selectedDashboardId.value) ?? OVERVIEW;
    },
    set(dashboard: Dashboard) {
      selectedDashboardId.value = dashboard.sail;
    },
  });
  const availableDashboards = computed(() =>
    selectedSails.value.filter((sail) => DASHBOARDS.some((d) => d.sail === sail.id)),
  );

  const currentVariables = computed(() =>
    selectedDashboard.value.groups.flatMap((g) => g.variables),
  );

  const selectedSailIds = useLocalStorage<SailId[]>("loads-variable-selected-sails", []);
  const selectedSails = computed<Sail<SailId>[]>({
    get() {
      return SAILS.filter((sail) => selectedSailIds.value.includes(sail.id));
    },
    set(sails: Sail<SailId>[]) {
      selectedSailIds.value = sails.map((sail) => sail.id);
    },
  });

  const getVariableById = <T extends number | boolean>(id: string) =>
    computed(() => variables.value.find((variable) => variable.id === id) as Variable<T>);

  const setAWA = (id: AWA) => {
    selectedAWA.value = id;
  };

  const setAWS = (id: NumRangeId) => {
    selectedAWS.value = id;
  };

  const setSelectedSails = (sails: Sail<SailId>[]) => {
    selectedSails.value = sails;

    // If the currently selected dashboard is not valid for the new sails, reset to OVERVIEW
    if (!sails.some((sail) => sail.id === selectedDashboardId.value)) {
      setDashboard(OVERVIEW);
    }
  };

  const setDashboard = (dashboard: Dashboard) => {
    selectedDashboard.value = dashboard;
  };

  const { data: definitions } = useQuery<QueryVariableDefinition>({
    query: VARIABLE_DEFINITIONS,
    context: LOADS_CONTEXT,
  });

  const { data: actuals, executeQuery: updateActuals } = useQuery<QueryVariableActual>({
    query: VARIABLE_ACTUALS,
    variables: {
      variables: currentVariables,
    },
    requestPolicy: "network-only",
    context: LOADS_CONTEXT,
  });

  const { data: referenceValues } = useQuery<QueryVariableReference>({
    query: VARIABLE_REFERENCE_VALUES,
    variables: {
      variables: currentVariables,
      sailset: selectedSailIds,
      awaRange: selectedAWA,
      awsRange: selectedAWS,
    },
    requestPolicy: "network-only",
    context: LOADS_CONTEXT,
  });

  const variables = computed<MaybeVariable[]>(() => {
    if (!definitions.value || !actuals.value || !referenceValues.value) {
      return [];
    }

    return currentVariables.value.map<MaybeVariable>((varId) => {
      const definition = definitions.value?.variables.find((def) => def.id === varId);
      const actual = actuals.value?.variables.find((act) => act.id === varId);
      const reference = referenceValues.value?.variables.find((ref) => ref.id === varId);
      return {
        id: varId,
        variable: definition?.variable,
        actual: actual?.actual,
        reference: reference?.reference,
      };
    });
  });

  const { resume: startPolling, pause: stopPolling } = useIntervalFn(
    updateActuals,
    UPDATE_INTERVAL_MS,
    {
      immediate: false,
    },
  );

  return {
    variables,
    getVariableById,
    selectedAWA,
    selectedAWS,
    setAWA,
    setAWS,
    selectedSails,
    setSelectedSails,
    selectedDashboard,
    setDashboard,
    availableDashboards,
    currentVariables,
    startPolling,
    stopPolling,
  };
});
