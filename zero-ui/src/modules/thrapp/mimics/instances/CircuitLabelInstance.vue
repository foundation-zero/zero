<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentInstanceProps } from ".";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListItem,
  ValueListSeparator,
} from "../components/value-list";
import { ModuleField } from "../providers";
import { FieldRenderer } from "../renderers";

/** Card with the heat, pump speed and temperature difference of one circuit inside an asset. */
withDefaults(
  defineProps<
    MimicComponentInstanceProps & {
      title: string;
      heatTransfer: ModuleField<SensorComponentType.HeatTransferDevice>;
      width?: number | string;
    }
  >(),
  { width: 164 },
);

const t = tScoped("thrapp.mimics.adsorption.chiller");
</script>

<template>
  <foreignObject
    :x="x"
    :y="y"
    :width="width"
    height="103"
  >
    <div class="bg-border-subtle flex h-full flex-col gap-1.25 rounded-[0.125rem] p-1">
      <header
        class="text-foreground font-heading text-center text-xs leading-6 font-bold tracking-wider uppercase"
      >
        {{ title }}
      </header>
      <!-- Rows are 14px high and 8px apart, like the separators' padding in the design. -->
      <ValueList
        dense
        class="gap-2 text-sm"
      >
        <ValueListSeparator class="my-0" />
        <ValueListHeatPowerItem
          class="h-3.5"
          :source="heatTransfer"
        />
        <ValueListItem class="h-3.5">
          <span class="text-brand">{{ t("pumpSpeed") }}</span>
          <span class="text-foreground font-medium"><FieldRenderer.Placeholder /></span>
        </ValueListItem>
        <ValueListDeltaTItem
          class="h-3.5"
          :source="heatTransfer"
        />
        <ValueListSeparator class="my-0" />
      </ValueList>
    </div>
  </foreignObject>
</template>
