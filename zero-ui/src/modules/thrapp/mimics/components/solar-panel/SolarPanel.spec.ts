import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { SolarPanelOrientation, SolarPanelSize, solarPanelPeakHeat, solarYieldColor } from ".";
import SolarPanel from "./SolarPanel.vue";

describe("solarPanelPeakHeat", () => {
  it("gives a large panel the design peak and a small one its share of the area", () => {
    expect(solarPanelPeakHeat()).toBe(360);
    expect(solarPanelPeakHeat(SolarPanelSize.Small)).toBeCloseTo((360 * 14) / 27);
  });
});

describe("solarYieldColor", () => {
  it("maps a low yield to the dark end and a high yield to the light end of the scale", () => {
    expect(solarYieldColor(0)).toBe("var(--color-accent-b-1000)");
    expect(solarYieldColor(0.5)).toBe("var(--color-accent-b-500)");
    expect(solarYieldColor(1)).toBe("var(--color-accent-b-0)");
  });

  it("clamps out-of-range yields", () => {
    expect(solarYieldColor(-1)).toBe("var(--color-accent-b-1000)");
    expect(solarYieldColor(2)).toBe("var(--color-accent-b-0)");
  });
});

describe("SolarPanel", () => {
  it("swaps the dimensions of a landscape panel", () => {
    const wrapper = mount(SolarPanel, {
      props: { size: SolarPanelSize.Small, orientation: SolarPanelOrientation.Landscape },
    });

    expect(wrapper.attributes("width")).toBe("36");
    expect(wrapper.attributes("height")).toBe("14");
  });
});
