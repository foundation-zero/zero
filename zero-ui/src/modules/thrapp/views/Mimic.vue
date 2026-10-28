<script setup lang="ts">
import {
  DynamicLegend,
  LegendTrigger,
  MIMIC_LEGEND_MAP,
} from "@/modules/thrapp/components/legends";
import {
  MimicViewport,
  MimicZoomProvider,
  ZoomControls,
} from "@/modules/thrapp/components/mimic-viewport";
import { MimicTooltipProvider } from "@/modules/thrapp/components/tooltip";
import NoopTooltipProvider from "@/modules/thrapp/components/tooltip/NoopTooltipProvider.vue";
import GridPattern from "@/modules/thrapp/mimics/modules/GridPattern.vue";
import { GraphQLProvider, MockProvider } from "@/modules/thrapp/mimics/providers";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { MIMICS, MimicKey } from "../router/mimics";

const demoMode = ref(false);
const provider = computed(() => (demoMode.value ? MockProvider : GraphQLProvider));

const { currentRoute } = useRouter();

const currentModule = computed(() => currentRoute.value.params.module as MimicKey);
const currentMimic = computed(() => MIMICS[currentModule.value]);
const currentLegend = computed(() => MIMIC_LEGEND_MAP[currentModule.value]);
</script>
<template>
  <component :is="provider">
    <MimicZoomProvider :key="currentModule">
      <section class="relative -mx-4 -mt-8 flex min-h-0 grow flex-col md:-mx-6 md:-mt-6 md:-mb-6">
        <GridPattern class="absolute top-0 right-0 bottom-0 left-0 h-full w-full" />

        <MimicTooltipProvider v-if="currentMimic">
          <!-- Keyed by module, so switching mimics starts again at fit-to-screen. -->

          <div class="relative z-1 min-h-0 min-w-0 flex-1">
            <MimicViewport class="size-full">
              <component :is="currentMimic.component" />
            </MimicViewport>
          </div>
        </MimicTooltipProvider>

        <footer
          class="absolute bottom-3 left-0 z-10 flex w-full items-center justify-between px-3 md:bottom-4 md:px-4"
        >
          <LegendTrigger v-if="currentLegend">
            <NoopTooltipProvider>
              <DynamicLegend :legend="currentLegend" />
            </NoopTooltipProvider>
          </LegendTrigger>

          &nbsp;

          <ZoomControls />
        </footer>
      </section>
    </MimicZoomProvider>
  </component>
</template>
