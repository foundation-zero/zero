import { extractProperty, toRecord } from "@/modules/common/lib/utils";
import { useQuery } from "@urql/vue";
import { useIntervalFn, useLocalStorage } from "@vueuse/core";
import { isBoolean } from "lodash";
import { defineStore } from "pinia";
import { computed } from "vue";
import { LOADS_CONTEXT } from "../graphql/client";
import { ALL_SAILS } from "../graphql/queries/sails";
import {
  VARIABLE_ACTUALS,
  VARIABLE_DEFINITIONS,
  VARIABLE_REFERENCE_VALUES,
} from "../graphql/queries/variables";
import { AWA_VALUES, AWS_VALUES } from "../lib/consts";
import {
  Dashboard,
  DASHBOARD_TYPES,
  DashboardId,
  DASHBOARDS,
  DashboardType,
  isDashboardType,
  OVERVIEW,
  VariableGroup,
} from "../lib/consts.dashboards";
import { POSITIONS_WITH_SAILS, SailId, SAILS } from "../lib/consts.sails";
import { findInRange, unique } from "../lib/utils";
import {
  AWA,
  CardType,
  MaybeVariable,
  NumRangeId,
  PositionId,
  Sail,
  SailPositionGroup,
  SailSelection,
  Variable,
} from "../types";
import {
  QuerySails,
  QueryVariableActual,
  QueryVariableDefinition,
  QueryVariableReference,
} from "../types/queries";

const UPDATE_INTERVAL_MS = 5000;

const toSupportedSailSelection = (
  storedValue: SailSelection,
  defaultValue: SailSelection,
): SailSelection =>
  toRecord(defaultValue, (position, defaultSail) =>
    storedValue[position] === null || POSITIONS_WITH_SAILS[position].includes(storedValue[position])
      ? storedValue[position]
      : defaultSail,
  );

const toSupportedValue =
  <T>(supportedValues: T[]) =>
  (storedValue: T, defaultValue: T): T =>
    supportedValues.includes(storedValue) ? storedValue : defaultValue;

const extractId = extractProperty("id");

export const useVariablesStore = defineStore("loads-variables", () => {
  const selectedCardType = useLocalStorage<CardType>("loads-variable-card-type", "numerical");

  /*** SAILS ***/

  const { data: sailsData } = useQuery<QuerySails>({
    query: ALL_SAILS,
    context: LOADS_CONTEXT,
  });

  const sails = computed<Sail<SailId>[]>(() => sailsData.value?.sails ?? []);

  const position = (name: string, ...positions: PositionId[]): SailPositionGroup => ({
    name,
    positions: positions.map((positionId) => ({
      sails: sails.value.filter((sail) => sail.positionId === positionId) ?? [],
      position: positionId,
    })),
  });

  const positionGroups = computed(() => [
    position("Mizzen", PositionId.Mizzen, PositionId.MizzenFore),
    position("Main", PositionId.Main),
    position("Headsails", PositionId.ForeInner, PositionId.ForeOuter),
  ]);

  const selectedSails = useLocalStorage<SailSelection>(
    "loads-variables-selected-sails",
    {
      [PositionId.Main]: null,
      [PositionId.ForeInner]: null,
      [PositionId.ForeOuter]: null,
      [PositionId.Mizzen]: null,
      [PositionId.MizzenFore]: null,
    },
    {
      writeDefaults: true,
      mergeDefaults: toSupportedSailSelection,
    },
  );

  const selectedSailIds = computed(() =>
    unique(selectedSails.value).filter((id) => !!id && SAILS.includes(id)),
  );

  const setSelectedSails = (sails: SailSelection) => {
    selectedSails.value = sails;

    if (isDashboardType(selectedDashboardId.value)) return;

    // If the currently selected dashboard is not valid for the new sailset, reset to OVERVIEW
    if (!selectedSailIds.value.includes(selectedDashboardId.value)) {
      setDashboard(OVERVIEW.id);
    }
  };

  /*** DASHBOARDS ***/
  const selectedAWA = useLocalStorage<AWA>("loads-variable-awa", AWA_VALUES[0].id, {
    writeDefaults: true,
    mergeDefaults: toSupportedValue(AWA_VALUES.map(extractId)),
  });
  const selectedAWS = useLocalStorage<NumRangeId>("loads-variable-aws", AWS_VALUES[0].id, {
    writeDefaults: true,
    mergeDefaults: toSupportedValue(AWS_VALUES.map(extractId)),
  });
  const selectedWindDirection = useLocalStorage<"port" | "starboard">(
    "loads-variable-wind-direction",
    "starboard",
    {
      writeDefaults: true,
      mergeDefaults: toSupportedValue(["port", "starboard"]),
    },
  );

  const selectedDashboardId = useLocalStorage<DashboardId>(
    "loads-variable-selected-dashboard",
    DashboardType.Static,
    {
      writeDefaults: true,
      mergeDefaults: toSupportedValue([...DASHBOARD_TYPES, ...SAILS]),
    },
  );

  const selectedDashboard = computed<Dashboard>({
    get() {
      return DASHBOARDS.find((d) => d.id === selectedDashboardId.value) ?? OVERVIEW;
    },
    set(dashboard: Dashboard) {
      selectedDashboardId.value = dashboard.id;
    },
  });

  const isDynamicDashboard = computed(() => selectedDashboardId.value === DashboardType.Dynamic);

  const visibleDashboardGroups = computed<VariableGroup[]>(() => {
    const dashboard = selectedDashboard.value;

    if (!isDynamicDashboard.value) {
      return dashboard.groups;
    } else {
      return dashboard.groups.filter((group) =>
        isBoolean(group.includeInDynamic)
          ? group.includeInDynamic
          : group.includeInDynamic.some((sail) => selectedSailIds.value.includes(sail)),
      );
    }
  });

  const availableDashboards = computed(() =>
    positionGroups.value
      .flatMap(({ positions }) => positions)
      .flatMap(({ sails }) => sails)
      .filter(
        (sail) =>
          selectedSailIds.value.includes(sail.id) && DASHBOARDS.some((d) => d.id === sail.id),
      ),
  );

  const setDashboard = (sail: DashboardId) => {
    selectedDashboardId.value = sail;
  };

  /*** VARIABLES ***/

  const currentVariables = computed(() =>
    // Always query for AWA and AWS
    selectedDashboard.value.groups
      .flatMap((g) => g.variables.map(([id]) => id))
      .concat(["awa", "aws"]),
  );

  const getVariableById = <T extends number | boolean>(id: string) =>
    computed(() => variables.value.find((variable) => variable.id === id) as Variable<T>);

  const { data: definitions } = useQuery<QueryVariableDefinition>({
    query: VARIABLE_DEFINITIONS,
    context: LOADS_CONTEXT,
  });

  const { data: actuals, executeQuery: updateActuals } = useQuery<QueryVariableActual>({
    query: VARIABLE_ACTUALS,
    variables: computed(() => ({
      variables: currentVariables.value,
    })),
    requestPolicy: "network-only",
    context: LOADS_CONTEXT,
  });

  const { data: referenceValues } = useQuery<QueryVariableReference>({
    query: VARIABLE_REFERENCE_VALUES,
    variables: computed(() => ({
      variables: currentVariables.value,
      sailset: selectedSailIds.value,
      awaRange: selectedAWA.value,
      awsRange: selectedAWS.value,
      windDirection: selectedWindDirection.value,
    })),
    requestPolicy: "network-only",
    context: LOADS_CONTEXT,
  });

  const variables = computed<MaybeVariable[]>(() => {
    if (!definitions.value) {
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

  /*** SETTINGS ***/

  const setAWA = (id: AWA) => {
    selectedAWA.value = id;
  };

  const setAWS = (id: NumRangeId) => {
    selectedAWS.value = id;
  };

  const setCardType = (type: CardType | null | undefined) => {
    if (type) {
      selectedCardType.value = type;
    }
  };

  const currentAWS = computed(
    () => actuals.value?.variables.find((v) => v.id === "aws")?.actual.value,
  );
  const currentAWA = computed(
    () => actuals.value?.variables.find((v) => v.id === "awa")?.actual.value,
  );

  const lockWindConditions = () => {
    selectedAWA.value = findInRange(currentAWA.value ?? 0, AWA_VALUES)?.id ?? selectedAWA.value;
    selectedAWS.value = findInRange(currentAWS.value ?? 0, AWS_VALUES)?.id ?? selectedAWS.value;
  };

  return {
    variables,
    getVariableById,
    selectedAWA,
    selectedAWS,
    selectedCardType,
    sails,
    positionGroups,
    setAWA,
    setAWS,
    setCardType,
    currentAWA,
    currentAWS,
    selectedSails,
    setSelectedSails,
    selectedDashboard,
    isDynamicDashboard,
    setDashboard,
    availableDashboards,
    visibleDashboardGroups,
    currentVariables,
    startPolling,
    stopPolling,
    lockWindConditions,
  };
});
