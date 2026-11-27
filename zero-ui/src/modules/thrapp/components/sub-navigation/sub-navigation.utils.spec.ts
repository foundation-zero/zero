import { MimicKey } from "@/modules/thrapp/router/mimics";
import { ControlStatus } from "@/modules/thrapp/stores/automation";
import { AmcsMode } from "@/modules/thrapp/types/thrs";
import { describe, expect, it } from "vitest";
import {
  getControlModule,
  getControlState,
  getModuleOptionGroups,
  getParentModule,
} from "./sub-navigation.utils";

const only =
  (...keys: MimicKey[]) =>
  (module: MimicKey) =>
    keys.includes(module);

describe("getModuleOptionGroups", () => {
  it("lists every module, grouped, when the page shows all of them", () => {
    expect(getModuleOptionGroups(() => true)).toEqual([
      {
        key: "producers",
        modules: [
          { key: "dc", disabled: false, subModules: ["dc-aft", "dc-ugrid", "dc-fwd"] },
          { key: "drives", disabled: false, subModules: ["drives-shorepower"] },
          { key: "pvt", disabled: false, subModules: ["pvt-main", "pvt-owners"] },
          { key: "thrusters", disabled: false, subModules: [] },
        ],
      },
      {
        key: "buffers",
        modules: [
          { key: "dhw", disabled: false, subModules: [] },
          { key: "pcm", disabled: false, subModules: [] },
        ],
      },
      { key: "consumers", modules: [{ key: "adsorption", disabled: false, subModules: [] }] },
    ]);
  });

  it("drops the modules the page cannot show and the groups left empty", () => {
    expect(getModuleOptionGroups(only("dhw", "pvt"))).toEqual([
      { key: "producers", modules: [{ key: "pvt", disabled: false, subModules: [] }] },
      { key: "buffers", modules: [{ key: "dhw", disabled: false, subModules: [] }] },
    ]);
  });

  it("keeps a module disabled when the page only shows some of its sub-modules", () => {
    expect(getModuleOptionGroups(only("pvt-owners"))).toEqual([
      {
        key: "producers",
        modules: [{ key: "pvt", disabled: true, subModules: ["pvt-owners"] }],
      },
    ]);
  });
});

describe("getParentModule", () => {
  it("finds the module of a sub-module", () => {
    expect(getParentModule("pvt-owners")).toBe("pvt");
  });

  it("has no parent for a module", () => {
    expect(getParentModule("pvt")).toBeUndefined();
  });
});

describe("getControlModule", () => {
  it("controls a sub-module through its module", () => {
    expect(getControlModule("pvt-owners")).toBe("pvt");
    expect(getControlModule("dhw")).toBe("dhw");
  });
});

describe("getControlState", () => {
  const status = (value: AmcsMode, automatic: boolean) =>
    ({
      modules: {
        dhw: {
          controlMode: { automatic, automaticMode: null },
          sensorValues: { mode: { mode: { value } } },
        },
      },
    }) as unknown as ControlStatus;

  it("is automatic or manual when the advisory mode is enabled", () => {
    expect(getControlState(status(AmcsMode.External, true), "dhw")).toBe("automatic");
    expect(getControlState(status(AmcsMode.External, false), "dhw")).toBe("manual");
  });

  it("is advisory disabled when the AMCS controls the module", () => {
    expect(getControlState(status(AmcsMode.Local, true), "dhw")).toBe("advisoryDisabled");
  });

  it("is unknown until the status of the module is loaded", () => {
    expect(getControlState(undefined, "dhw")).toBeUndefined();
    expect(getControlState(status(AmcsMode.External, true), "pvt")).toBeUndefined();
  });

  it("is unknown while the control mode of the module is missing", () => {
    const withoutControlMode = {
      modules: {
        dhw: {
          controlMode: null,
          sensorValues: { mode: { mode: { value: AmcsMode.External } } },
        },
      },
    } as unknown as ControlStatus;

    expect(getControlState(withoutControlMode, "dhw")).toBeUndefined();
    expect(getControlState(status(AmcsMode.External, true), undefined)).toBeUndefined();
  });
});
