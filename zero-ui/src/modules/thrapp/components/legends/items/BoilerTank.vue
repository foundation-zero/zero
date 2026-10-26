<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../mimics/data";
import BoilerTankInstance from "../../../mimics/instances/BoilerTankInstance.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend/";

const t = tScoped("thrapp.legends.boilerTank");
const boilerTank = getTooltipContext(MimicComponentType.BoilerTank)("1053");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <BoilerTankInstance v-bind="boilerTank" />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>
        {{ t("description") }}
      </LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
