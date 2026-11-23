<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <g>
    <!-- The four converters form one shore power unit. -->
    <rect
      x="21.99"
      y="0.5"
      width="306.76"
      height="849.93"
      rx="15.5"
      fill="#F4F9FE"
      fill-opacity="0.05"
      stroke="#EE44DD"
      stroke-opacity="0.55"
      stroke-dasharray="2 2"
    />
    <text
      x="175.37"
      y="15.76"
      text-anchor="middle"
      class="fill-muted-foreground"
      font-family="Inter"
      font-size="12"
    >
      {{ t("thrapp.mimics.drives.sections.oneUnit") }}
    </text>
  </g>
</template>
