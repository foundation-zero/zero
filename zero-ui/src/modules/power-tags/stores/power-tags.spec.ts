import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useQuery } from "@urql/vue";
import { setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";
import { POWER_TAG_PANELS } from "../graphql/queries/power-tag-panels";
import type { PowerTag, PowerTagPanel, PowerTagValues } from "../types";
import { usePowerTagsStore } from "./power-tags";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
}));

const queries = createUseQueryFake();
const panelsQuery = () => queries.resultOf<{ powerTagPanels: PowerTagPanel[] }>(POWER_TAG_PANELS);

const NO_READINGS = Object.fromEntries(
  [
    "currentA",
    "currentB",
    "currentC",
    "currentN",
    "voltageAn",
    "voltageBn",
    "voltageCn",
    "activePowerA",
    "activePowerB",
    "activePowerC",
    "activePowerTotal",
    "powerFactorA",
    "powerFactorB",
    "powerFactorC",
    "powerFactorTotal",
  ].map((key) => [key, null]),
) as unknown as PowerTagValues;

const tag = (
  topic: string,
  {
    component = null,
    consumer = null,
  }: { component?: string | null; consumer?: string | null } = {},
  values: Partial<PowerTagValues> = {},
): PowerTag => ({
  topic,
  metadata: {
    panel: null,
    slug: null,
    component,
    consumer,
    values: [{ name: "activePowerTotal", unit: "W" }],
  },
  values: { ...NO_READINGS, ...values },
});

const panel = (id: string, ...powerTags: PowerTag[]) => ({ id, powerTags }) as PowerTagPanel;

describe("power tags store", () => {
  beforeEach(() => {
    queries.reset();
    vi.mocked(useQuery).mockImplementation(queries.useQuery);
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  it("sorts panels by id and their tags by component, consumer and topic", () => {
    const store = usePowerTagsStore();

    panelsQuery().data.value = {
      powerTagPanels: [
        panel(
          "panel-b",
          tag("t3", { component: "pump", consumer: "b" }),
          tag("t2", { component: "pump", consumer: "a" }),
          tag("t1", { component: "pump", consumer: "a" }),
          tag("t0", { component: "fan" }),
        ),
        panel("panel-a"),
      ],
    };

    expect(store.sortedPanels.map(({ id }) => id)).toEqual(["panel-a", "panel-b"]);
    expect(store.sortedPanels[1].powerTags.map(({ topic }) => topic)).toEqual([
      "t0",
      "t1",
      "t2",
      "t3",
    ]);
  });

  it("selects the first panel and moves on when the selected panel disappears", async () => {
    const store = usePowerTagsStore();

    panelsQuery().data.value = { powerTagPanels: [panel("b"), panel("a")] };
    await nextTick();
    expect(store.activePanel).toBe("a");

    store.activePanel = "b";
    panelsQuery().data.value = { powerTagPanels: [panel("b"), panel("c")] };
    await nextTick();
    expect(store.activePanel).toBe("b");

    panelsQuery().data.value = { powerTagPanels: [panel("c")] };
    await nextTick();
    expect(store.activePanel).toBe("c");

    panelsQuery().data.value = { powerTagPanels: [] };
    await nextTick();
    expect(store.activePanel).toBe("");
  });

  it("shows the tags, units and missing-readings state of the active panel", async () => {
    const store = usePowerTagsStore();

    panelsQuery().data.value = {
      powerTagPanels: [panel("a", tag("t1"), tag("t2", {}, { activePowerTotal: 120 }))],
    };
    await nextTick();

    expect(store.activePowerTags.map(({ topic }) => topic)).toEqual(["t1", "t2"]);
    expect(store.unitByName).toEqual({ activePowerTotal: "W" });
    expect(store.allReadingsNull).toBe(false);

    panelsQuery().data.value = { powerTagPanels: [panel("a", tag("t1"), tag("t2"))] };

    expect(store.allReadingsNull).toBe(true);
  });

  it("shows only total power until all columns are requested", () => {
    const store = usePowerTagsStore();

    expect(store.visibleColumns.map(({ key }) => key)).toEqual(["activePowerTotal"]);

    store.showAll = true;

    expect(store.visibleColumns).toHaveLength(15);
  });

  it("refreshes from the network", () => {
    usePowerTagsStore().refresh();

    expect(panelsQuery().executeQuery).toHaveBeenCalledWith({ requestPolicy: "network-only" });
  });
});
