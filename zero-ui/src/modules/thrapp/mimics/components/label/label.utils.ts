import { computed, MaybeRefOrGetter, toValue } from "vue";
import { LayerFilterOption, useLayerFilterContext } from "../layer-filter/layer-filter.provider";

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
