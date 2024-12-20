export interface LightControl {
  name: string;
  on: boolean;
  brightness: number;
}

export interface Room {
  name: string;
  lights: LightControl[];
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
