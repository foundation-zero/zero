export { default as SplashScreen } from "./SplashScreen.vue";

import { INCLUDED_APPS, ZeroApps } from "@/apps.ts";
import {
  RiBarChart2Line,
  RiLightbulbLine,
  RiPlugLine,
  RiSailboatLine,
  RiTempHotLine,
  RiWindyLine,
} from "@remixicon/vue";
import type { Component } from "vue";

export type SplashAppLink = {
  id: ZeroApps;
  nameKey: string;
  to: string;
  icon: Component;
  iconBackground: string;
  glow: string;
  border: string;
  shadow: string;
};

// These timings were arbitrarily chosen by CoPilot but seem to work well together.
export const TILE_ANIMATION_INTERVAL = 120; // ms
export const TILE_INITIAL_DELAY = 240; // ms
export const HERO_KICKER_DELAY = 120; // ms
export const HERO_KICKER_DURATION = 700; // ms
export const HERO_DESCRIPTION_DELAY = 720; // ms
export const HERO_DESCRIPTION_DURATION = 700; // ms
export const HERO_LETTERS_DURATION = 640; // ms
export const HERO_LETTERS_INTERVAL = 120; // ms
export const HERO_LETTERS_INITIAL_DELAY = 240; // ms

export const SPLASH_LETTERS = ["Z", "E", "R", "O"];

export const SPLASH_APP_LINKS: SplashAppLink[] = [
  {
    id: ZeroApps.loads,
    nameKey: "views.splash.apps.loads.title",
    to: "/loads",
    icon: RiWindyLine,
    glow: "color-mix(in srgb, var(--brand-dull) 42%, transparent)",
    border: "var(--brand-dull)",
    shadow: "var(--brand-dull)",
    iconBackground: "color-mix(in srgb, var(--brand) 18%, transparent)",
  },
  {
    id: ZeroApps.thrsim,
    nameKey: "views.splash.apps.thrsim.title",
    to: "/thrsim",
    icon: RiTempHotLine,
    glow: "color-mix(in srgb, var(--warning-dull) 38%, transparent)",
    border: "var(--warning-dull)",
    shadow: "var(--warning-dull)",
    iconBackground: "color-mix(in srgb, var(--warning) 16%, transparent)",
  },
  {
    id: ZeroApps.thrs,
    nameKey: "views.splash.apps.thrs.title",
    to: "/thrs",
    icon: RiTempHotLine,
    glow: "color-mix(in srgb, var(--warning-dull) 38%, transparent)",
    border: "var(--warning-dull)",
    shadow: "var(--warning-dull)",
    iconBackground: "color-mix(in srgb, var(--warning) 16%, transparent)",
  },
  {
    id: ZeroApps.domestic,
    nameKey: "views.splash.apps.domestic.title",
    to: "/domestic",
    icon: RiLightbulbLine,
    glow: "color-mix(in srgb, var(--constructive-dull) 38%, transparent)",
    border: "var(--constructive-dull)",
    shadow: "var(--constructive-dull)",
    iconBackground: "color-mix(in srgb, var(--constructive) 16%, transparent)",
  },
  {
    id: ZeroApps.grafana,
    nameKey: "views.splash.apps.grafana.title",
    to: "/grafana",
    icon: RiBarChart2Line,
    glow: "color-mix(in srgb, var(--warning-dull) 36%, transparent)",
    border: "var(--warning-dull)",
    shadow: "var(--warning-dull)",
    iconBackground: "color-mix(in srgb, var(--warning) 16%, transparent)",
  },
  {
    id: ZeroApps.sailSystem,
    nameKey: "views.splash.apps.sailSystem.title",
    descriptionKey: "views.splash.apps.sailSystem.description",
    to: "/sail-system",
    icon: RiSailboatLine,
    glow: "color-mix(in srgb, var(--brand-dull) 40%, transparent)",
    border: "var(--brand-dull)",
    shadow: "var(--brand-dull)",
    iconBackground: "color-mix(in srgb, var(--brand) 16%, transparent)",
  },
  {
    id: ZeroApps.powerTags,
    nameKey: "views.splash.apps.powerTags.title",
    to: "/power-tags",
    icon: RiPlugLine,
    glow: "color-mix(in srgb, var(--brand-dull) 42%, transparent)",
    border: "var(--brand-dull)",
    shadow: "var(--brand-dull)",
    iconBackground: "color-mix(in srgb, var(--brand) 18%, transparent)",
  },
].filter((app) => INCLUDED_APPS.includes(app.id));
