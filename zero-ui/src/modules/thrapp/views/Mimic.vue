<script setup lang="ts">
import Label from "@/components/ui/label/Label.vue";
import { Switch } from "@/components/ui/switch";
import {
  DynamicLegend,
  LegendTrigger,
  MIMIC_LEGEND_MAP,
} from "@/modules/thrapp/components/legends";
import { MimicViewport } from "@/modules/thrapp/components/mimic-viewport";
import { MimicTooltipProvider } from "@/modules/thrapp/components/tooltip";
import NoopTooltipProvider from "@/modules/thrapp/components/tooltip/NoopTooltipProvider.vue";
import GridPattern from "@/modules/thrapp/mimics/modules/GridPattern.vue";
import { GraphQLProvider, MockProvider } from "@/modules/thrapp/mimics/providers";
import { ENV } from "@/settings";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { MIMICS, MimicKey } from "../router/mimics";

const demoMode = ref(false);
const provider = computed(() => (demoMode.value ? MockProvider : GraphQLProvider));

const { currentRoute } = useRouter();
const { t } = useI18n();

const currentModule = computed(() => currentRoute.value.params.module as MimicKey);
const currentMimic = computed(() => MIMICS[currentModule.value]);
const currentLegend = computed(() => MIMIC_LEGEND_MAP[currentModule.value]);
const showDemoMode = computed(() => ENV.VITE_SHOW_DEMO_MODE === "1");
</script>
<template>
  <component :is="provider">
    <section
      class="relative flex h-full justify-around gap-x-4 max-lg:flex-col-reverse portrait:flex-col-reverse"
    >
      <GridPattern class="absolute top-0 right-0 bottom-0 left-0 h-full w-full" />
      <aside
        class="z-1 flex w-full flex-row-reverse items-center justify-between overflow-hidden landscape:lg:w-62.5 landscape:lg:flex-col landscape:lg:items-start"
        :class="{ 'justify-between': showDemoMode, 'justify-end': !showDemoMode }"
      >
        <div
          v-if="showDemoMode"
          class="flex items-center gap-3"
        >
          <Switch v-model="demoMode" />
          <Label>{{ t("thrapp.labels.demoMode") }}</Label>
        </div>

        <LegendTrigger v-if="currentLegend">
          <NoopTooltipProvider>
            <DynamicLegend :legend="currentLegend" />
          </NoopTooltipProvider>
        </LegendTrigger>
      </aside>

      <MimicTooltipProvider v-if="currentMimic">
        <!-- Keyed by module, so switching mimics starts again at fit-to-screen. -->
        <MimicViewport
          :key="currentModule"
          class="z-1 min-h-0 min-w-0 flex-1"
        >
          <component :is="currentMimic.component" />
        </MimicViewport>
      </MimicTooltipProvider>
    </section>
  </component>
</template>
