export interface LightControl {
  name: string;
  on: boolean;
  brightness: number;
}

export interface BlindsControl {
  name: string;
  position: number;
}

export interface Room {
  name: string;
  lights: ControlGroup<LightControl>[];
  blinds: ControlGroup<BlindsControl>[];
}

export interface ShipArea {
  name: string;
  rooms: Room[];
}

export interface Breakpoints {
  tablet: boolean;
  phone: boolean;
  landscape: boolean;
  portrait: boolean;
  mobile: boolean;
  desktop: boolean;
}

export interface ControlGroup<T> {
  name: string;
  controls: T[];
}

export type LightGroup = ControlGroup<LightControl>;
export type BlindsGroup = ControlGroup<BlindsControl>;
