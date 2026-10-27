import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useQuery } from "@urql/vue";
import { setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { VARIABLE_ACTUALS, VARIABLE_DEFINITIONS } from "../graphql/queries/variables";
import { DASHBOARDS, DashboardType, OVERVIEW } from "../lib/consts.dashboards";
import { SailId } from "../lib/consts.sails";
import { AWA, PositionId, SailSelection } from "../types";
import { QueryVariableActual, QueryVariableDefinition } from "../types/queries";
import { useVariablesStore } from "./variables";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
}));

const queries = createUseQueryFake();

const sailSelection = (selection: Partial<SailSelection>): SailSelection => ({
  [PositionId.Main]: null,
  [PositionId.ForeInner]: null,
  [PositionId.ForeOuter]: null,
  [PositionId.Mizzen]: null,
  [PositionId.MizzenFore]: null,
  ...selection,
});

describe("loads variables store", () => {
  beforeEach(() => {
    localStorage.clear();
    queries.reset();
    vi.mocked(useQuery).mockImplementation(queries.useQuery);
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  it("falls back to the overview when the stored dashboard no longer exists", () => {
    localStorage.setItem("loads-variable-selected-dashboard", "removed-dashboard");

    expect(useVariablesStore().selectedDashboard).toBe(OVERVIEW);
  });

  describe("selecting sails", () => {
    it("returns to the overview when the selected sail dashboard is no longer in the sailset", () => {
      const store = useVariablesStore();
      store.setSelectedSails(sailSelection({ [PositionId.ForeOuter]: SailId.A2 }));
      store.setDashboard(SailId.A2);

      store.setSelectedSails(sailSelection({ [PositionId.ForeOuter]: SailId.A3 }));

      expect(store.selectedDashboard).toBe(OVERVIEW);
    });

    it("keeps the selected sail dashboard while that sail stays in the sailset", () => {
      const store = useVariablesStore();
      store.setSelectedSails(sailSelection({ [PositionId.ForeOuter]: SailId.A2 }));
      store.setDashboard(SailId.A2);

      store.setSelectedSails(
        sailSelection({ [PositionId.ForeOuter]: SailId.A2, [PositionId.Main]: SailId.FullMain }),
      );

      expect(store.selectedDashboard.id).toBe(SailId.A2);
    });

    it("keeps the dynamic dashboard whatever sails are selected", () => {
      const store = useVariablesStore();
      store.setDashboard(DashboardType.Dynamic);

      store.setSelectedSails(sailSelection({ [PositionId.Main]: SailId.Trisail }));

      expect(store.selectedDashboard.id).toBe(DashboardType.Dynamic);
    });
  });

  it("always queries wind conditions, plus the overhoist of each mast lock it shows", () => {
    const store = useVariablesStore();
    const withMastLocks = DASHBOARDS.find((dashboard) =>
      dashboard.groups.some((group) => group.variables.some(([id]) => id === "mast-lock-main-1")),
    )!;
    store.setDashboard(withMastLocks.id);

    expect(store.currentVariables).toEqual(expect.arrayContaining(["awa", "aws"]));
    expect(store.currentVariables).toContain("mast-overhoist-main-1");
    // boom locks have no overhoist counterpart
    expect(store.currentVariables).toContain("mast-lock-main-boom-1");
    expect(store.currentVariables).not.toContain("mast-overhoist-main-boom-1");
  });

  it("combines definitions and actuals per variable", () => {
    const store = useVariablesStore();
    queries.resultOf<QueryVariableDefinition>(VARIABLE_DEFINITIONS).data.value = {
      variables: [{ id: "aws", variable: { name: "AWS" } }],
    } as unknown as QueryVariableDefinition;
    queries.resultOf<QueryVariableActual>(VARIABLE_ACTUALS).data.value = {
      variables: [{ id: "aws", actual: { value: 12 } }],
    } as unknown as QueryVariableActual;

    expect(store.variables.find(({ id }) => id === "aws")).toEqual({
      id: "aws",
      variable: { name: "AWS" },
      actual: { value: 12 },
      reference: undefined,
    });
  });

  it("locks the wind range to the current wind conditions", () => {
    const store = useVariablesStore();
    queries.resultOf<QueryVariableActual>(VARIABLE_ACTUALS).data.value = {
      variables: [
        { id: "awa", actual: { value: 95 } },
        { id: "aws", actual: { value: 12 } },
      ],
    } as unknown as QueryVariableActual;

    store.lockWindConditions();

    expect(store.selectedAWA).toBe(AWA.Downwind);
    expect(store.selectedAWS).toBe("aws_10_15");
  });
});
