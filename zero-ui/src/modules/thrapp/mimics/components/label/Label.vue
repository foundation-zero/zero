<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes, useSlots } from "vue";
import { LabelProps } from ".";
import { LABEL_PLACEMENT_ALIGNMENT, LabelPlacement } from "./label.consts";
import { getLabelPlacement, useLabelTarget, useLabelVisibility } from "./label.utils";

const props = withDefaults(
  defineProps<
    {
      class?: HTMLAttributes["class"];
    } & LabelProps
  >(),
  {
    x: 0,
    width: 80,
    height: 40,
    targetX: 0,
    targetWidth: 0,
    minWidth: 35,
  },
);

const slots = useSlots();
const { showTag, showValue, isVisible } = useLabelVisibility({
  hasValue: () => !!slots.value,
  unfiltered: () => props.unfiltered,
});

const centred = computed(() => props.targetWidth != 0 && props.targetX != 0);
const labelX = computed(() =>
  Number(props.x) > 0
    ? Number(props.x)
    : Number(props.targetX) + Number(props.targetWidth) / 2 - Number(props.width) / 2,
);

const target = useLabelTarget();
const placement = computed(() => {
  if (!target?.value) return LabelPlacement.Below;

  const contentX = centred.value
    ? labelX.value + Number(props.width) / 2
    : labelX.value + Number(props.minWidth) / 2;

  return getLabelPlacement({ x: contentX, y: Number(props.y ?? 0) }, target.value);
});
// A centred label beside its component (a negative target width) still aligns towards it.
const centredOnTarget = computed(
  () => centred.value && [LabelPlacement.Above, LabelPlacement.Below].includes(placement.value),
);
</script>

<template>
  <svg
    v-show="isVisible"
    :width="width"
    :height="height"
    :x="labelX"
    :y="y"
  >
    <!-- Offset on y needed because of hgroup positioning within the foreignObject -->
    <foreignObject
      :width="width"
      :height="height"
    >
      <div
        class="h-full w-full"
        :class="{ 'flex flex-col items-center': centred }"
      >
        <!--
          The label is stacked on an invisible copy of its full content, so hiding the tag or value
          shrinks it towards its component instead of leaving a gap. The copy comes first, so the
          baseline the label sits on doesn't move either.
        -->
        <div class="inline-grid">
          <hgroup
            v-for="placeholder in [true, false]"
            :key="String(placeholder)"
            xmlns="http://www.w3.org/1999/xhtml"
            :aria-hidden="placeholder || undefined"
            :class="
              cn(
                'bg-background col-start-1 row-start-1 inline-flex min-w-8 flex-col rounded-[0.125rem] px-1',
                props.class,
                placeholder
                  ? 'invisible'
                  : [
                      LABEL_PLACEMENT_ALIGNMENT[placement],
                      centredOnTarget && 'justify-self-center',
                    ],
              )
            "
            :style="{
              minWidth: (placeholder ? $slots['value'] : showValue) ? minWidth + 'px' : undefined,
            }"
          >
            <header
              v-show="placeholder || showTag"
              class="text-muted-foreground text-3xs"
            >
              <slot />
            </header>
            <p
              v-if="$slots['value']"
              v-show="placeholder || showValue"
              class="text-foreground text-xs font-medium"
            >
              <slot name="value" />
            </p>
          </hgroup>
        </div>
      </div>
    </foreignObject>
  </svg>
</template>
