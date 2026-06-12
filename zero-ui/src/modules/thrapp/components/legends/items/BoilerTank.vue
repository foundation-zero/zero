<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { BOILERS_MIMIC_DATA } from "@/modules/thrapp/mimics/modules/boilers/data/index.ts";
import { MimicComponentType } from "@/modules/thrapp/types/index.ts";
import BoilerTankInstance from "../../../mimics/instances/BoilerTankInstance.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend/";

const t = tScoped("thrapp.legends.boilerTank");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <BoilerTankInstance v-bind="BOILERS_MIMIC_DATA[MimicComponentType.BoilerTank][1053]" />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>
        {{ t("description") }}
      </LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
