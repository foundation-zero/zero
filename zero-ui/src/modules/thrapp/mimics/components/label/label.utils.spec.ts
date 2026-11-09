import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { defineComponent, h, nextTick, ref } from "vue";
import { LabelPlacement } from "./label.consts";
import { LabelTarget } from "./label.types";
import {
  getLabelPlacement,
  provideLabelTarget,
  registerLabelTarget,
  useLabelTarget,
} from "./label.utils";

const TARGET: LabelTarget = { x: 100, y: 100, width: 40, height: 40 };

describe("getLabelPlacement", () => {
  it.each([
    { anchor: { x: 120, y: 60 }, placement: LabelPlacement.Above },
    { anchor: { x: 120, y: 150 }, placement: LabelPlacement.Below },
    { anchor: { x: 60, y: 110 }, placement: LabelPlacement.Start },
    { anchor: { x: 160, y: 110 }, placement: LabelPlacement.End },
  ])("places a label anchored at $anchor.x,$anchor.y $placement", ({ anchor, placement }) => {
    expect(getLabelPlacement(anchor, TARGET)).toBe(placement);
  });

  it("places a label anchored on the edge of its target beside it", () => {
    expect(getLabelPlacement({ x: 100, y: 60 }, TARGET)).toBe(LabelPlacement.Start);
    expect(getLabelPlacement({ x: 140, y: 60 }, TARGET)).toBe(LabelPlacement.End);
  });
});

describe("label target", () => {
  const Part = defineComponent(() => {
    registerLabelTarget({ x: 0, y: 0, width: 1, height: 1 });

    return () => null;
  });

  const Component = defineComponent({
    props: { box: { type: Object, required: true }, nested: Boolean },
    setup(props) {
      registerLabelTarget(() => props.box as LabelTarget);

      return () => (props.nested ? h(Part) : null);
    },
  });

  const mountInstance = (box: LabelTarget, nested = false) => {
    let target: ReturnType<typeof provideLabelTarget> | undefined;
    const Instance = defineComponent(() => {
      target = provideLabelTarget();

      return () => h(Component, { box, nested });
    });
    mount(Instance);

    return target!;
  };

  it("collects the box of the component", () => {
    expect(mountInstance(TARGET).value).toEqual(TARGET);
  });

  it("ignores components nested inside the component", () => {
    expect(mountInstance(TARGET, true).value).toEqual(TARGET);
  });

  it("follows the component when it moves", async () => {
    const box = ref(TARGET);
    let target: ReturnType<typeof provideLabelTarget> | undefined;
    const Instance = defineComponent(() => {
      target = provideLabelTarget();

      return () => h(Component, { box: box.value });
    });
    mount(Instance);

    box.value = { ...TARGET, x: 200 };
    await nextTick();

    expect(target!.value?.x).toBe(200);
  });

  it("has no target outside an instance", () => {
    let target: ReturnType<typeof useLabelTarget> | undefined;
    mount(
      defineComponent(() => {
        target = useLabelTarget();

        return () => null;
      }),
    );

    expect(target).toBeNull();
  });
});
