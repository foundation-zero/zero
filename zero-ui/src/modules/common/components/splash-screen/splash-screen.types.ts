import { ZeroApps } from "@/apps.ts";
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
  /** Shown on the corner of the tile's icon, for what needs attention in the app. */
  badge?: Component;
};
