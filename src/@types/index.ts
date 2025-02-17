import { Blinds, LightingGroups } from "@/gql/graphql";

export interface Room {
  id: string;
  name: string;
  lights: LightGroup[];
  blinds: BlindsGroup[];
}

export interface ShipArea {
  name: string;
  group: RoomGroup;
  rooms: Room[];
}

export const enum RoomGroup {
  AFT = "AFT",
  MID = "MID",
  FORE = "FORE",
  UPPERDECK = "UPPERDECK",
  HALLWAYS = "HALLWAYS",
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

export type LightGroup = ControlGroup<LightingGroups>;
export type BlindsGroup = ControlGroup<Blinds>;
