import { INCLUDED_APPS, ZeroApps } from "@/apps.ts";
import { ZiHydrogenerator } from "@common/components/icons";
import {
  RiCheckboxCircleLine,
  RiCompass3Line,
  RiFlashlightLine,
  RiLightbulbAiLine,
  RiPlugLine,
  RiRouteLine,
  RiSailboatLine,
  RiSteering2Line,
  RiTempHotLine,
} from "@remixicon/vue";
import type { SplashEntry, SplashEntryMotion, SplashGroup } from "./splash-screen.types";

/** Ripple entry from the launcher motion prototype: tiles scale up from the screen centre outward. */
export const RIPPLE_HEAD_DURATION = 240; // ms
export const RIPPLE_TILE_DURATION = 300; // ms
export const RIPPLE_DELAY_PER_PIXEL = 0.32; // ms
export const RIPPLE_SCALE_REDUCTION = 0.12;
export const RIPPLE_EASING = "cubic-bezier(.2,1.15,.4,1)";
/** Matches the centre of the background glow and grid. */
export const RIPPLE_ORIGIN = { x: 0.5, y: 0.54 };

/** Phones always get small tiles. */
export const SPLASH_PHONE_WIDTH = 560; // px

export const WORDMARK_DURATION = 1400; // ms
export const WORDMARK_EASING = "cubic-bezier(.45,.05,.35,1)";

/** Coming back from an app is shorter and calmer than a cold start. */
export const SPLASH_ENTRY_MOTION: Record<SplashEntry, SplashEntryMotion> = {
  cold: { duration: 1, delay: 1, distance: 1 },
  return: { duration: 0.55, delay: 0.35, distance: 0.5 },
};

/** Tiles without an app are planned apps, shown disabled as "Coming soon". */
const ALL_SPLASH_GROUPS: SplashGroup[] = [
  {
    nameKey: "views.splash.groups.sailing",
    tiles: [
      {
        app: ZeroApps.loads,
        to: "/loads",
        nameKey: "views.splash.apps.loads.title",
        icon: RiSailboatLine,
      },
      { nameKey: "views.splash.apps.conning.title", icon: RiCompass3Line },
      { nameKey: "views.splash.apps.weatherRouting.title", icon: RiRouteLine },
      {
        app: ZeroApps.sailSystem,
        to: "/sail-system",
        nameKey: "views.splash.apps.sailSystem.title",
        icon: RiSteering2Line,
      },
    ],
  },
  {
    nameKey: "views.splash.groups.energy",
    tiles: [
      {
        app: ZeroApps.thrs,
        to: "/thrs",
        nameKey: "views.splash.apps.thrs.title",
        icon: RiTempHotLine,
      },
      {
        app: ZeroApps.thrsim,
        to: "/thrsim",
        nameKey: "views.splash.apps.thrsim.title",
        icon: RiTempHotLine,
      },
      {
        app: ZeroApps.grafana,
        to: "/grafana/energy-monitoring",
        nameKey: "views.splash.apps.energyMonitoring.title",
        icon: RiFlashlightLine,
      },
      {
        app: ZeroApps.grafana,
        to: "/grafana/hydrogeneration",
        nameKey: "views.splash.apps.hydrogeneration.title",
        icon: ZiHydrogenerator,
      },
      {
        app: ZeroApps.powerTags,
        to: "/power-tags",
        nameKey: "views.splash.apps.powerTags.title",
        icon: RiPlugLine,
      },
    ],
  },
  {
    nameKey: "views.splash.groups.shipSystems",
    tiles: [
      {
        app: ZeroApps.domestic,
        to: "/domestic",
        nameKey: "views.splash.apps.domestic.title",
        icon: RiLightbulbAiLine,
      },
      {
        app: ZeroApps.grafana,
        to: "/grafana/commissioning",
        nameKey: "views.splash.apps.commissioning.title",
        icon: RiCheckboxCircleLine,
      },
    ],
  },
];

export const SPLASH_GROUPS: SplashGroup[] = ALL_SPLASH_GROUPS.map((group) => ({
  ...group,
  tiles: group.tiles.filter((tile) => !tile.app || INCLUDED_APPS.includes(tile.app)),
})).filter((group) => group.tiles.length);
