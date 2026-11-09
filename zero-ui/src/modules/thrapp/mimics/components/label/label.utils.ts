import {
  computed,
  inject,
  InjectionKey,
  MaybeRefOrGetter,
  provide,
  ShallowRef,
  shallowRef,
  toValue,
  watchEffect,
} from "vue";
import { LayerFilterOption, useLayerFilterContext } from "../layer-filter/layer-filter.provider";
import { LabelPlacement } from "./label.consts";
import { LabelTarget } from "./label.types";

/** Which parts of a label the yard tag and sensor value filters leave visible. */
export const useLabelVisibility = ({
  hasValue = true,
  unfiltered = false,
}: {
  hasValue?: MaybeRefOrGetter<boolean>;
  unfiltered?: MaybeRefOrGetter<boolean>;
} = {}) => {
  const { isFilterActive } = useLayerFilterContext();

  const showTag = computed(() => toValue(unfiltered) || isFilterActive(LayerFilterOption.YardTags));
  const showValue = computed(
    () => toValue(unfiltered) || isFilterActive(LayerFilterOption.SensorValues),
  );
  const isVisible = computed(() => showTag.value || (showValue.value && toValue(hasValue)));

  return { showTag, showValue, isVisible };
};

const LABEL_TARGET_KEY: InjectionKey<ShallowRef<LabelTarget | undefined> | null> =
  Symbol("LabelTarget");

/** Collects the box of the component that the labels rendered next to it belong to. */
export const provideLabelTarget = () => {
  const target = shallowRef<LabelTarget>();
  provide(LABEL_TARGET_KEY, target);

  return target;
};

/**
 * Registers a component as the target of the labels next to it. Components nested inside it are
 * parts of the same component, so only the outermost one registers.
 */
export const registerLabelTarget = (box: MaybeRefOrGetter<LabelTarget>) => {
  const target = inject(LABEL_TARGET_KEY, null);
  provide(LABEL_TARGET_KEY, null);

  if (target) watchEffect(() => (target.value = toValue(box)));
};

/** The box of the component a label belongs to, if it is rendered next to one. */
export const useLabelTarget = () => inject(LABEL_TARGET_KEY, null);

/**
 * The side of its component a label sits on. The anchor is the horizontal centre of the label's
 * content (it starts at the label's x, or is centred on the target) and the top of the label.
 */
export const getLabelPlacement = (
  anchor: Readonly<{ x: number; y: number }>,
  { x, y, width }: LabelTarget,
): LabelPlacement => {
  if (anchor.x > x && anchor.x < x + width) {
    return anchor.y < y ? LabelPlacement.Above : LabelPlacement.Below;
  }

  return anchor.x < x + width / 2 ? LabelPlacement.Start : LabelPlacement.End;
};
