import { PositionId, Sail, SailPositionGroup } from "../types";

const position = (name: string, ...positions: PositionId[]): SailPositionGroup => ({
  name,
  positions: positions.map((positionId) => ({
    sails: POSITIONS_WITH_SAILS[positionId],
    position: positionId,
  })),
});

export const sail = (name: string, id: SailId): Sail<SailId> => ({
  name,
  id,
});

export const enum SailId {
  None = "none",
  FullMain = "full_main",
  MainReef1 = "main_reef1",
  MainReef2 = "main_reef2",
  MainReef3 = "main_reef3",
  Trisail = "trisail",
  UtilityMain = "utility_main",
  FullMizzen = "full_mizzen",
  MizzenReef1 = "mizzen_reef1",
  MizzenReef2 = "mizzen_reef2",
  Blade = "blade",
  CodeZero = "code_zero",
  A3 = "A3",
  A2 = "A2",
  Staysail = "staysail",
  StormJib = "storm_jib",
  MizzenJib = "mizzen_jib",
  MizzenStaysail = "mizzen_staysail",
}

const POSITIONS_WITH_SAILS: Record<PositionId, Sail<SailId>[]> = {
  [PositionId.Main]: [
    sail("Full Main", SailId.FullMain),
    sail("Main R1", SailId.MainReef1),
    sail("Main R2", SailId.MainReef2),
    sail("Main R3", SailId.MainReef3),
    sail("Utility Main", SailId.UtilityMain),
    sail("Main Trisail", SailId.Trisail),
  ],
  [PositionId.ForeInner]: [
    sail("Blade", SailId.Blade),
    sail("Storm Jib", SailId.StormJib),
    sail("Staysail", SailId.Staysail),
  ],
  [PositionId.ForeOuter]: [
    sail("Code-0", SailId.CodeZero),
    sail("A3", SailId.A3),
    sail("A2", SailId.A2),
  ],
  [PositionId.Mizzen]: [
    sail("Full Mizzen", SailId.FullMizzen),
    sail("Mizzen R1", SailId.MizzenReef1),
    sail("Mizzen R2", SailId.MizzenReef2),
  ],
  [PositionId.MizzenFore]: [
    sail("Mizzen Jib", SailId.MizzenJib),
    sail("Mizzen Staysail", SailId.MizzenStaysail),
  ],
};

export const SAILS = Object.values(POSITIONS_WITH_SAILS).flat();

export const POSITION_GROUPS: SailPositionGroup[] = [
  position("Main", PositionId.Main),
  position("Mizzen", PositionId.Mizzen, PositionId.MizzenFore),
  position("Foresails", PositionId.ForeInner, PositionId.ForeOuter),
];
