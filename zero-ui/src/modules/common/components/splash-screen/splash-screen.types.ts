import { ZeroApps } from "@/apps.ts";
import type { Component } from "vue";

export type SplashEntry = "cold" | "return";

type SplashTileBase = {
  nameKey: string;
  icon: Component;
};

export type SplashAppTile = SplashTileBase & {
  app: ZeroApps;
  to: string;
};

export type SplashComingSoonTile = SplashTileBase & {
  app?: never;
  to?: never;
};

export type SplashTile = SplashAppTile | SplashComingSoonTile;

export type SplashGroup = {
  nameKey: string;
  tiles: SplashTile[];
};

export type SplashSize = "l" | "m" | "s";

export type SplashFit = {
  size: SplashSize;
  columns: number;
};

export type SplashEntryMotion = {
  duration: number;
  delay: number;
  distance: number;
};
