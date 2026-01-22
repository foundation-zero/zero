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
  Blade = "blade",
  CodeZero = "code_zero",
  Genoa = "genoa",
  Gennaker = "gennaker",
  Staysail = "staysail",
  StormJib = "storm_jib",
  FullMizzen = "full_mizzen",
  MizzenReef1 = "mizzen_reef1",
  MizzenReef2 = "mizzen_reef2",
  MizzenGenoa = "mizzen_genoa",
  MizzenJib = "mizzen_jib",
}

const POSITIONS_WITH_SAILS: Record<PositionId, Sail<SailId>[]> = {
  [PositionId.Main]: [
    sail("Full", SailId.FullMain),
    sail("R1", SailId.MainReef1),
    sail("R2", SailId.MainReef2),
    sail("R3", SailId.MainReef3),
    sail("Tri", SailId.Trisail),
  ],
  [PositionId.ForeInner]: [
    sail("Blade", SailId.Blade),
    sail("Code-0", SailId.CodeZero),
    sail("Furling Genoa", SailId.Genoa),
    sail("Gennaker", SailId.Gennaker),
  ],
  [PositionId.ForeOuter]: [sail("Staysail", SailId.Staysail), sail("Storm Jib", SailId.StormJib)],
  [PositionId.Mizzen]: [
    sail("Full", SailId.FullMizzen),
    sail("R1", SailId.MizzenReef1),
    sail("R2", SailId.MizzenReef2),
  ],
  [PositionId.MizzenFore]: [
    sail("Mizzen Genoa", SailId.MizzenGenoa),
    sail("Mizzen Jib", SailId.MizzenJib),
  ],
};

export const SAILS = Object.values(POSITIONS_WITH_SAILS).flat();

export const POSITION_GROUPS: SailPositionGroup[] = [
  position("Main", PositionId.Main),
  position("Foresails", PositionId.ForeInner, PositionId.ForeOuter),
  position("Mizzen", PositionId.Mizzen, PositionId.MizzenFore),
];
