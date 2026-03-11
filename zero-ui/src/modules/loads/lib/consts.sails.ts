import { PositionId } from "../types";

export const enum SailId {
  None = "none",
  FullMain = "full-main",
  MainReef1 = "main-reef1",
  MainReef2 = "main-reef2",
  MainReef3 = "main-reef3",
  Trisail = "trisail",
  UtilityMain = "utility-main",
  FullMizzen = "full-mizzen",
  MizzenReef1 = "mizzen-reef1",
  MizzenReef2 = "mizzen-reef2",
  Blade = "blade",
  CodeZero = "code-zero",
  A3 = "A3",
  A2 = "A2",
  Staysail = "staysail",
  StormJib = "storm-jib",
  MizzenJib = "mizzen-jib",
  MizzenStaysail = "mizzen-staysail",
}

export const POSITIONS_WITH_SAILS: Record<PositionId, SailId[]> = {
  [PositionId.Main]: [
    SailId.FullMain,
    SailId.MainReef1,
    SailId.MainReef2,
    SailId.MainReef3,
    SailId.UtilityMain,
    SailId.Trisail,
  ],
  [PositionId.ForeInner]: [SailId.Blade, SailId.Staysail, SailId.StormJib],
  [PositionId.ForeOuter]: [SailId.A2, SailId.A3, SailId.CodeZero],
  [PositionId.Mizzen]: [SailId.FullMizzen, SailId.MizzenReef1, SailId.MizzenReef2],
  [PositionId.MizzenFore]: [SailId.MizzenStaysail, SailId.MizzenJib],
};

export const SAILS = Object.values(POSITIONS_WITH_SAILS).flat();
