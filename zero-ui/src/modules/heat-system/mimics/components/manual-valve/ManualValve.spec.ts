import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { ManualValveType } from ".";
import { ComponentOrientation } from "..";
import ManualValve from "./ManualValve.vue";

describe("ManualValve", () => {
  it.each([
    { type: ManualValveType.Switch, paths: 2, circles: 2 },
    { type: ManualValveType.FlowControl, paths: 3, circles: 1 },
    { type: ManualValveType.ThreeWay, paths: 3, circles: 2 },
  ])("preserves the $type fallback geometry", ({ type, paths, circles }) => {
    const wrapper = mount(ManualValve, { props: { type } });

    expect(wrapper.findAll("path")).toHaveLength(paths);
    expect(wrapper.findAll("circle")).toHaveLength(circles);
    expect(wrapper.findAll("path")[0].attributes("d")).toBe("M18 18L6 26L6 10L18 18Z");
    expect(wrapper.findAll("path")[1].attributes("d")).toBe("M18 18L30 10L30 26L18 18Z");
    expect(wrapper.find('[data-slot="manual-flow-marker"]').exists()).toBe(false);
  });

  it("defaults to the switch marker", () => {
    const wrapper = mount(ManualValve);

    expect(wrapper.findAll("circle")).toHaveLength(2);
    expect(wrapper.find("circle").attributes("r")).toBe("3.5");
  });

  it("allows body and marker composition without rendering fallback shapes", () => {
    const wrapper = mount(ManualValve, {
      slots: {
        default: '<path data-test="body" d="M0 0L1 1" />',
        marker: '<circle data-test="marker" cx="18" cy="18" r="1" />',
      },
    });

    expect(wrapper.findAll("path")).toHaveLength(1);
    expect(wrapper.findAll("circle")).toHaveLength(1);
    expect(wrapper.find('[data-test="body"]').exists()).toBe(true);
    expect(wrapper.find('[data-test="marker"]').exists()).toBe(true);
  });

  it("keeps the exact manual flow marker upright when orientation changes", async () => {
    const wrapper = mount(ManualValve, {
      props: { type: ManualValveType.Flow, orientation: ComponentOrientation.Right },
    });
    const marker = wrapper.find('[data-slot="manual-flow-marker"]');

    expect(marker.attributes("style")).toContain("rotate(-90deg)");
    expect(marker.find("circle").attributes("r")).toBe("2.5");
    expect(marker.find("line").attributes("x2")).toBe("9.18376");
    expect(marker.find("path").attributes("d")).toBe(
      "M15.991 10.4209L17.4149 11.8448L18.0225 9.81325L15.991 10.4209Z",
    );

    await wrapper.setProps({ orientation: ComponentOrientation.Left });

    expect(marker.attributes("style")).toContain("rotate(-270deg)");
  });
});
