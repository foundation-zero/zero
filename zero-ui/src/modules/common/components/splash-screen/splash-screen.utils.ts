import {
  RIPPLE_DELAY_PER_PIXEL,
  RIPPLE_EASING,
  RIPPLE_HEAD_DURATION,
  RIPPLE_ORIGIN,
  RIPPLE_SCALE_REDUCTION,
  RIPPLE_TILE_DURATION,
  SPLASH_ENTRY_MOTION,
  SPLASH_PHONE_WIDTH,
  WORDMARK_DURATION,
  WORDMARK_EASING,
} from "./splash-screen.consts";
import type { SplashEntry, SplashFit, SplashSize } from "./splash-screen.types";

let hasEntered = false;

/** The first visit after a page load is a cold start; every later visit returns from an app. */
export const takeSplashEntry = (): SplashEntry => {
  const entry = hasEntered ? "return" : "cold";
  hasEntered = true;
  return entry;
};

export const resetSplashEntry = () => {
  hasEntered = false;
};

export const rippleDelay = (distance: number, entry: SplashEntry) =>
  distance * RIPPLE_DELAY_PER_PIXEL * SPLASH_ENTRY_MOTION[entry].delay;

/** Group headings fade in while tiles scale up from the screen centre outward. */
export const playRipple = (root: HTMLElement, entry: SplashEntry): Animation[] => {
  const motion = SPLASH_ENTRY_MOTION[entry];
  const originX = window.innerWidth * RIPPLE_ORIGIN.x;
  const originY = window.innerHeight * RIPPLE_ORIGIN.y;
  const scale = 1 - RIPPLE_SCALE_REDUCTION * motion.distance;

  const heads = [...root.querySelectorAll<HTMLElement>("[data-splash-head]")].map((head) =>
    head.animate([{ opacity: 0 }, { opacity: 1 }], {
      duration: RIPPLE_HEAD_DURATION * motion.duration,
      easing: "ease-out",
      fill: "backwards",
    }),
  );

  const tiles = [...root.querySelectorAll<HTMLElement>("[data-splash-tile]")].map((tile) => {
    const rect = tile.getBoundingClientRect();
    const distance = Math.hypot(
      rect.left + rect.width / 2 - originX,
      rect.top + rect.height / 2 - originY,
    );
    return tile.animate(
      [
        { opacity: 0, transform: `scale(${scale})` },
        { opacity: 1, transform: "none" },
      ],
      {
        duration: RIPPLE_TILE_DURATION * motion.duration,
        delay: rippleDelay(distance, entry),
        easing: RIPPLE_EASING,
        fill: "backwards",
      },
    );
  });

  return [...heads, ...tiles];
};

const applyFit = (fit: SplashFit, screen: HTMLElement) => {
  screen.dataset.splashSize = fit.size;
  screen.style.setProperty("--splash-columns", String(fit.columns));
};

/**
 * Picks the largest tile size, and for it the most compact tiles per row, at which the launcher
 * fits the screen without scrolling. When nothing fits, the smallest size scrolls vertically.
 */
export const fitSplash = (screen: HTMLElement, header: HTMLElement, area: HTMLElement) => {
  const groups = area.firstElementChild as HTMLElement | null;
  const clusters = [...(groups?.children ?? [])] as HTMLElement[];
  if (!groups || !clusters.length) return;
  delete groups.dataset.stacked;

  const tileCounts = clusters.map(
    (cluster) => cluster.querySelectorAll("[data-splash-tile]").length,
  );
  const maxColumns = Math.max(...tileCounts);
  const sizes: SplashSize[] = screen.clientWidth <= SPLASH_PHONE_WIDTH ? ["s"] : ["l", "m", "s"];

  const measure = (fit: SplashFit) => {
    applyFit(fit, screen);
    const style = getComputedStyle(area);
    const width = area.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
    const height =
      screen.clientHeight -
      header.offsetHeight -
      parseFloat(style.paddingTop) -
      parseFloat(style.paddingBottom);
    const widest = Math.max(groups.scrollWidth, ...clusters.map((cluster) => cluster.scrollWidth));
    return {
      ...fit,
      fitsWidth: widest <= width + 1,
      fitsHeight: groups.offsetHeight <= height + 1,
      height: groups.offsetHeight,
    };
  };
  // The minimums below keep groups from collapsing into thin columns beside each other. They can't
  // overflow: a group is never wider than the screen, so its tiles wrap when fewer fit in a row.
  const columnRange = (min: number) =>
    Array.from({ length: Math.max(maxColumns - min + 1, 0) }, (_, index) => maxColumns - index);
  const mostCompact = (fits: ReturnType<typeof measure>[]) =>
    fits.toSorted((first, second) => first.height - second.height)[0];

  const best =
    sizes
      .map((size) =>
        mostCompact(
          columnRange(Math.min(3, maxColumns))
            .map((columns) => measure({ size, columns }))
            .filter((fit) => fit.fitsWidth && fit.fitsHeight),
        ),
      )
      .find(Boolean) ??
    mostCompact(
      columnRange(2)
        .map((columns) => measure({ size: "s", columns }))
        .filter((fit) => fit.fitsWidth),
    ) ??
    ({ size: "s", columns: 2 } satisfies SplashFit);

  applyFit(best, screen);

  // When every group has a row of its own, line them up on one left edge at one width.
  const rows = new Set(clusters.map((cluster) => cluster.offsetTop));
  if (clusters.length > 1 && rows.size === clusters.length) groups.dataset.stacked = "";
};

/** Writes the wordmark by drawing the pen stroke that masks it. */
export const drawWordmark = (pen: SVGPathElement): Animation =>
  pen.animate([{ strokeDashoffset: 1 }, { strokeDashoffset: 0 }], {
    duration: WORDMARK_DURATION,
    easing: WORDMARK_EASING,
    fill: "both",
  });
