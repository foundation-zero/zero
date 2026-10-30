<script setup lang="ts">
import { SensorComponentType, SensorDefinitionMap } from "@/modules/thrapp/types/thrs";
import { RiArrowLeftLine, RiArrowRightLine } from "@remixicon/vue";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";

/**
 * Temperature where a circuit enters or leaves an asset. `side` is the asset edge the label sits
 * on: the arrow points out of the asset for the outgoing temperature and into it for the incoming
 * one, and is drawn on the outer side of the text.
 */
const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps & {
      temperature: ModuleField<SensorComponentType.HeatTransferDevice>;
      field: keyof SensorDefinitionMap[SensorComponentType.HeatTransferDevice];
      port: "in" | "out";
      side?: "left" | "right";
    }
  >(),
  { side: "right" },
);

const { t } = useI18n();

const pointsRight = computed(() => (props.side === "right") === (props.port === "out"));
</script>

<template>
  <foreignObject
    :x="x"
    :y="y"
    width="49"
    height="35"
  >
    <div
      class="bg-muted flex h-full flex-col items-center justify-center gap-0.75 p-1"
      :class="port === 'in' && 'flex-col-reverse'"
    >
      <span
        class="text-brand text-2xs flex items-center leading-2.5"
        :class="side === 'left' && 'flex-row-reverse'"
      >
        {{ t("units.temp") }}{{ t(`temperatureLabels.${port}`) }}
        <RiArrowRightLine
          v-if="pointsRight"
          class="size-3"
        />
        <RiArrowLeftLine
          v-else
          class="size-3"
        />
      </span>
      <SensorValue
        :source="temperature"
        :field="field"
      >
        <span class="text-muted-foreground text-xs leading-3 text-nowrap">
          <FieldRenderer.Temperature />
        </span>
      </SensorValue>
    </div>
  </foreignObject>
</template>
