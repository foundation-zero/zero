import { beforeEach, describe, expect, it } from "vitest";
import { RIPPLE_DELAY_PER_PIXEL } from "./splash-screen.consts";
import { fitSplash, resetSplashEntry, rippleDelay, takeSplashEntry } from "./splash-screen.utils";

describe("takeSplashEntry", () => {
  beforeEach(resetSplashEntry);

  it("starts cold on the first visit and returns on later visits", () => {
    expect(takeSplashEntry()).toBe("cold");
    expect(takeSplashEntry()).toBe("return");
    expect(takeSplashEntry()).toBe("return");
  });
});

describe("rippleDelay", () => {
  it("grows with the distance from the ripple origin", () => {
    expect(rippleDelay(0, "cold")).toBe(0);
    expect(rippleDelay(500, "cold")).toBe(500 * RIPPLE_DELAY_PER_PIXEL);
  });

  it("is shorter when returning from an app", () => {
    expect(rippleDelay(500, "return")).toBeLessThan(rippleDelay(500, "cold"));
  });
});

/** jsdom has no layout, so the launcher lays itself out with a simple flex-wrap model. */
const CELL = { l: 200, m: 160, s: 120 } as const;
const ROW = { l: 240, m: 200, s: 160 } as const;
const HEAD = 60;
const HEADER = 100;

const stub = (element: Element, properties: Record<string, () => number>) =>
  Object.entries(properties).forEach(([name, get]) =>
    Object.defineProperty(element, name, { configurable: true, get }),
  );

const mountLauncher = (width: number, height: number, tileCounts: number[]) => {
  const screen = document.createElement("div");
  const header = document.createElement("header");
  const area = document.createElement("div");
  const groups = document.createElement("div");
  area.style.padding = "0px";
  screen.append(header, area);
  area.append(groups);

  const clusters = tileCounts.map((count) => {
    const cluster = document.createElement("section");
    cluster.append(
      ...Array.from({ length: count }, () => {
        const tile = document.createElement("div");
        tile.setAttribute("data-splash-tile", "");
        return tile;
      }),
    );
    groups.append(cluster);
    return cluster;
  });

  const size = () => (screen.dataset.splashSize ?? "l") as keyof typeof CELL;
  const columns = () => Number(screen.style.getPropertyValue("--splash-columns"));
  const clusterWidth = (count: number) => Math.min(columns(), count) * CELL[size()];
  const clusterHeight = (count: number) => HEAD + Math.ceil(count / columns()) * ROW[size()];

  /** Groups wrap onto a new row when the next one doesn't fit the width. */
  const layout = () => {
    const rows: { width: number; height: number; members: number[] }[] = [];
    tileCounts.forEach((count, index) => {
      const row = rows[rows.length - 1];
      const clusterW = clusterWidth(count);
      if (row && row.width + clusterW <= width) {
        row.width += clusterW;
        row.height = Math.max(row.height, clusterHeight(count));
        row.members.push(index);
      } else {
        rows.push({ width: clusterW, height: clusterHeight(count), members: [index] });
      }
    });
    return rows;
  };

  stub(screen, { clientWidth: () => width, clientHeight: () => height });
  stub(header, { offsetHeight: () => HEADER });
  stub(area, { clientWidth: () => width });
  stub(groups, {
    scrollWidth: () => Math.max(...layout().map((row) => row.width)),
    offsetHeight: () => layout().reduce((total, row) => total + row.height, 0),
  });
  clusters.forEach((cluster, index) =>
    stub(cluster, {
      scrollWidth: () => clusterWidth(tileCounts[index]),
      offsetTop: () => layout().findIndex((row) => row.members.includes(index)),
    }),
  );

  fitSplash(screen, header, area);
  return {
    size: screen.dataset.splashSize,
    columns: columns(),
    stacked: groups.dataset.stacked !== undefined,
  };
};

describe("fitSplash", () => {
  it("uses the largest tiles when everything fits", () => {
    expect(mountLauncher(3000, 1200, [4, 5, 2])).toMatchObject({ size: "l", columns: 5 });
  });

  it("wraps tiles into fewer columns before shrinking them", () => {
    // Groups stack at five columns but fit side by side at three.
    expect(mountLauncher(1300, 1200, [4, 5, 2])).toMatchObject({ size: "l" });
  });

  it("shrinks the tiles when the largest size doesn't fit the height", () => {
    expect(mountLauncher(1300, 600, [4, 5, 2]).size).toBe("m");
  });

  it("falls back to the shortest layout of the smallest tiles when nothing fits", () => {
    // Two columns let all three groups share one row, which scrolls the least.
    expect(mountLauncher(800, 300, [4, 5, 2])).toMatchObject({ size: "s", columns: 2 });
  });

  it("always uses the smallest tiles on a phone", () => {
    expect(mountLauncher(390, 2000, [4, 5, 2])).toMatchObject({ size: "s", columns: 3 });
  });

  it("lines groups up when each has a row of its own", () => {
    expect(mountLauncher(500, 2000, [4, 5, 2]).stacked).toBe(true);
    expect(mountLauncher(3000, 1200, [4, 5, 2]).stacked).toBe(false);
  });
});
