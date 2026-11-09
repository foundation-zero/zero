import i18n from "@/i18n";
import { ControlStatus } from "@/modules/thrapp/stores/automation";
import { AmcsControlMode, DcMode, PvtMode } from "@/modules/thrapp/types/thrs";
import { describe, expect, it } from "vitest";
import { NamedValue } from "vue-i18n";
import { ModeBadgeMode } from "./mode-badge.consts";
import { getModuleModes } from "./mode-badge.utils";

const t = (key: string, values?: NamedValue) =>
  i18n.global.t(`thrapp.mimics.modeBadge.${key}`, values ?? {});

const amcs = (value: AmcsControlMode) => ({ mode: { mode: { value } } });

const withModule = (module: string, status: object) =>
  ({ modules: { [module]: status } }) as unknown as ControlStatus;

const automatic = (module: string, automaticMode: object | null) =>
  withModule(module, {
    controlMode: { automatic: !!automaticMode, automaticMode },
    sensorValues: amcs(AmcsControlMode.External),
  });

const labels = (module: Parameters<typeof getModuleModes>[0], control?: ControlStatus) =>
  getModuleModes(module, control, t).map(({ label }) => label);

describe("getModuleModes", () => {
  it("prefixes each PVT target, front to back and then the owners", () => {
    const control = automatic("pvt", {
      fwd: { mode: PvtMode.Recovery },
      aft: { mode: PvtMode.Recovery },
      owners: { mode: PvtMode.Idle },
    });

    expect(getModuleModes("pvt", control, t)).toEqual([
      { mode: ModeBadgeMode.Using, label: "FW - Recovery" },
      { mode: ModeBadgeMode.Using, label: "AFT - Recovery" },
      { mode: ModeBadgeMode.Idle, label: "Owners - Idle" },
    ]);
  });

  it("prefixes each DC converter group", () => {
    const control = automatic("dc", {
      brightloopsAft: { mode: DcMode.Idle },
      brightloopsFwd: { mode: DcMode.Recovery },
      ugrids: { mode: DcMode.Idle },
    });

    expect(labels("dc", control)).toEqual(["AFT - Idle", "FWD - Recovery", "Ugrids - Idle"]);
  });

  it("shows the modes of a single-target module without a prefix", () => {
    const control = automatic("dhw", {
      boostingMode: "boosting_high_temperature",
      fillingMode: "filling",
    });

    expect(getModuleModes("dhw", control, t)).toEqual([
      { mode: ModeBadgeMode.Boosting, label: "Boosting HT" },
      { mode: ModeBadgeMode.Filling, label: "Filling" },
    ]);
  });

  it("shows one manual control badge per target under manual control", () => {
    expect(getModuleModes("pvt", automatic("pvt", null), t)).toEqual([
      { mode: ModeBadgeMode.ManualControl, label: "FW - Manual control" },
      { mode: ModeBadgeMode.ManualControl, label: "AFT - Manual control" },
      { mode: ModeBadgeMode.ManualControl, label: "Owners - Manual control" },
    ]);
    expect(labels("thrusters", automatic("thrusters", null))).toEqual(["Manual control"]);
  });

  it("names the AMCS mode when the advisory mode is disabled", () => {
    const control = withModule("pvt", { sensorValues: amcs(AmcsControlMode.Manual) });

    expect(getModuleModes("pvt", control, t)).toEqual([
      { mode: ModeBadgeMode.AdvisoryOff, label: "AMCS manual" },
    ]);
  });

  it("falls back to the generic advisory off badge while the status is unknown", () => {
    expect(getModuleModes("pvt", undefined, t)).toEqual([
      { mode: ModeBadgeMode.AdvisoryOff, label: undefined },
    ]);
  });
});
