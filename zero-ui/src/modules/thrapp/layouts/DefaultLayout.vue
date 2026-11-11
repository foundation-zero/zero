<script setup lang="ts">
import { ThrappHeader } from "@/modules/thrapp/components/navigation";
import { getControlModule } from "@/modules/thrapp/components/sub-navigation";
import { client } from "@/modules/thrapp/graphql/client";
import { MimicKey } from "@/modules/thrapp/router/mimics";
import { provideClient } from "@urql/vue";
import { computed, provide } from "vue";
import { useRoute } from "vue-router";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const currentRoute = useRoute();
const modules: Array<MimicKey> = [
  "dhw",
  "thrusters",
  "pvt",
  "pvt-main",
  "pvt-owners",
  "pvt-main-heat",
  "pcm",
  "dc",
  "drives",
  "adsorption",
];
const currentTabKey = computed(() => currentRoute.params.module as MimicKey);

// The header and the page share the control module: sub-modules (e.g. the PVT biminis) are
// controlled through their parent module.
provide(
  "currentModule",
  computed(() => currentTabKey.value && getControlModule(currentTabKey.value)),
);
</script>

<template>
  <!-- The header sits in the flow, so a sub navigation of any height pushes the page down. -->
  <div class="flex h-svh flex-col">
    <ThrappHeader>
      <component
        :is="currentRoute.meta.subNavigation"
        v-if="currentRoute.meta.subNavigation"
        :modules="modules"
        :active-module="currentTabKey"
      />
    </ThrappHeader>
    <main class="flex min-h-0 flex-1 flex-col overflow-y-auto">
      <Suspense>
        <article class="flex min-h-0 flex-1 flex-col px-4 pt-4 md:p-6">
          <slot />
        </article>
      </Suspense>
    </main>
  </div>
</template>
