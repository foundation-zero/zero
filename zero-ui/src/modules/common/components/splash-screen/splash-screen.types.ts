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
};
