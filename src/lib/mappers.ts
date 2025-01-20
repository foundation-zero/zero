import { BlindsControl, BlindsGroup, LightControl, LightGroup } from "@/@types";

export const toLightControl = (name: string): LightControl => ({
  name,
  on: true,
  brightness: Math.random() * 100,
});

export const toLightGroup =
  (...controls: string[]) =>
  (name: string): LightGroup => ({ name, controls: controls.map(toLightControl) });

export const toBlindsControl = (name: string): BlindsControl => ({
  name,
  position: Math.random() * 100,
});

export const toBlindsGroup =
  (...controls: string[]) =>
  (name: string): BlindsGroup => ({ name, controls: controls.map(toBlindsControl) });
