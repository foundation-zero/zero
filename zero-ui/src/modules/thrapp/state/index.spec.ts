import { AmcsControlMode, DcMode, PvtMode } from "@/modules/thrsim/types";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createApp, reactive, ref } from "vue";
import { useAdvisoryEnabled, useAutomaticMode, useDcMode, usePvtMode } from ".";

const setModuleAutomation = vi.fn();
const automation = reactive({
  control: undefined as unknown,
  setAutomatedControl: vi.fn(() => setModuleAutomation),
});

vi.mock("@/modules/thrsim/stores/automation", () => ({
  useAutomationStore: () => automation,
}));

const currentModule = ref<string | undefined>("dhw");

// useAutomaticMode and useAdvisoryEnabled inject the module that is currently shown
const inModule = <T>(composable: () => T): T => {
  const app = createApp({});
  app.provide("currentModule", currentModule);
  return app.runWithContext(composable);
};

const stamp = <T>(value: T) => ({ value, timestamp: new Date() });

describe("thrapp state", () => {
  beforeEach(() => {
    automation.control = undefined;
    automation.setAutomatedControl.mockClear();
    setModuleAutomation.mockReset();
    currentModule.value = "dhw";
  });

  describe("usePvtMode", () => {
    it("reads the automatic mode of the given PVT group", () => {
      automation.control = {
        modules: {
          pvt: {
            controlMode: {
              automaticMode: { aft: { mode: PvtMode.Warmup }, fwd: { mode: PvtMode.Recovery } },
            },
          },
        },
      };

      expect(usePvtMode("aft").value).toBe(PvtMode.Warmup);
      expect(usePvtMode("fwd").value).toBe(PvtMode.Recovery);
    });

    it("falls back to idle while the control status is not loaded", () => {
      expect(usePvtMode("aft").value).toBe(PvtMode.Idle);
    });
  });

  describe("useDcMode", () => {
    it("reads the automatic mode of the given converter group", () => {
      automation.control = {
        modules: {
          dc: { controlMode: { automaticMode: { ugrids: { mode: DcMode.Recovery } } } },
        },
      };

      expect(useDcMode("ugrids").value).toBe(DcMode.Recovery);
    });

    it("falls back to idle when the group has no mode", () => {
      automation.control = { modules: { dc: { controlMode: { automaticMode: {} } } } };

      expect(useDcMode("brightloopsAft").value).toBe(DcMode.Idle);
    });
  });

  describe("useAutomaticMode", () => {
    it("reads whether the current module is in automatic mode", () => {
      automation.control = {
        modules: {
          dhw: { controlMode: { automatic: true } },
          pvt: { controlMode: { automatic: false } },
        },
      };
      const automatic = inModule(useAutomaticMode);

      expect(automatic.value).toBe(true);

      currentModule.value = "pvt";
      expect(automatic.value).toBe(false);
    });

    it("is undefined while the control status is not loaded", () => {
      expect(inModule(useAutomaticMode).value).toBeUndefined();
    });

    it("switches the automation mode of the current module when set", () => {
      const automatic = inModule(useAutomaticMode);

      automatic.value = false;

      expect(automation.setAutomatedControl).toHaveBeenCalledWith("dhw");
      expect(setModuleAutomation).toHaveBeenCalledWith(false);
    });
  });

  describe("useAdvisoryEnabled", () => {
    const withAmcsMode = (mode: AmcsControlMode) => ({
      modules: { dhw: { sensorValues: { mode: { mode: stamp(mode) } } } },
    });

    it("is enabled when the AMCS hands control to us", () => {
      automation.control = withAmcsMode(AmcsControlMode.External);

      expect(inModule(useAdvisoryEnabled).value).toBe(true);
    });

    it.each([AmcsControlMode.Local, AmcsControlMode.Manual, AmcsControlMode.Auto])(
      "is disabled when the AMCS is in %s mode",
      (mode) => {
        automation.control = withAmcsMode(mode);

        expect(inModule(useAdvisoryEnabled).value).toBe(false);
      },
    );

    it.each([
      {
        case: "no module is selected",
        module: undefined,
        control: withAmcsMode(AmcsControlMode.External),
      },
      { case: "the control status is not loaded", module: "dhw", control: undefined },
      { case: "the module has no sensor values", module: "dhw", control: { modules: { dhw: {} } } },
    ])("is unknown when $case", ({ module, control }) => {
      currentModule.value = module;
      automation.control = control;

      expect(inModule(useAdvisoryEnabled).value).toBeNull();
    });
  });
});
