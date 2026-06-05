<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { SensorComponentType } from "@/modules/thrs/types";
import BoilerTankInstance from "../../../mimics/instances/BoilerTankInstance.vue";
import { getField } from "../../../mimics/providers";
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
      <BoilerTankInstance
        :title="t('assetTitle')"
        tag-id="1053"
        :level="getField(SensorComponentType.Level, 'boilers', 'boilersLevelTank1')"
        :temperature="
          getField(SensorComponentType.Temperature, 'boilers', 'boilersTemperatureTank1')
        "
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>
        {{ t("description") }}
      </LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
