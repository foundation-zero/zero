<script lang="ts">
import { GraphType } from ".";
</script>
<script setup lang="ts">
import { TooltipListItem } from "@/modules/thrapp/components/tooltip-list";
import { ENV } from "@/settings";
import { computed } from "vue";

const props = withDefaults(
  defineProps<{ type: string; device?: string; field: string | string[]; graphType?: GraphType }>(),
  {},
);

const grafanaBaseUrl = computed(() => (ENV.VITE_GRAFANA_URL ?? "").trim());

const iframeSrc = computed(() => {
  if (!grafanaBaseUrl.value || !props.device) return "";

  const now = new Date();
  let yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);

  const url = new URL(`${grafanaBaseUrl.value}/d-solo/adzxbs2/thrs-ui-embed`);
  url.searchParams.set("orgId", "1");
  url.searchParams.set("timezone", "browser");
  url.searchParams.set("from", yesterday.getTime().toString());
  url.searchParams.set("to", now.getTime().toString());
  url.searchParams.set("var-type", props.type);
  url.searchParams.set("var-device", props.device);
  if (Array.isArray(props.field)) {
    props.field.forEach((value) => url.searchParams.append("var-field", value));
  } else {
    url.searchParams.set("var-field", props.field);
  }
  url.searchParams.set("panelId", props.graphType ?? GraphType.TIMESERIES);
  url.searchParams.set("__feature.dashboardSceneSolo", "true");
  return url.toString();
});
</script>

<template>
  <TooltipListItem
    v-if="iframeSrc"
    class="w-full"
  >
    <iframe
      :src="iframeSrc"
      class="w-full border-0"
      width="100%"
      height="300"
      loading="lazy"
      referrerpolicy="strict-origin-when-cross-origin"
      :title="`Sensor graph ${props.field}`"
    ></iframe>
  </TooltipListItem>
</template>
