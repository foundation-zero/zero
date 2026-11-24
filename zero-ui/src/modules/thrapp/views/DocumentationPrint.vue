<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { tScoped } from "@/modules/common/lib/utils";
import { ManualDocument } from "@/modules/thrapp/components/manual";
import { RiArrowLeftLine, RiPrinterLine } from "@remixicon/vue";
import { computedAsync } from "@vueuse/core";
import { computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { DOCUMENTATION } from "../router/documentation";
import { MimicKey } from "../router/mimics";

const t = tScoped("thrapp.views.documentation");

const route = useRoute();
const loadManual = computed(() => DOCUMENTATION[route.params.module as MimicKey]);
const html = computedAsync(async () => loadManual.value?.());

// The crew's copy is printed light, whatever theme the screen is in.
const root = document.documentElement;
const wasDark = root.classList.contains("dark");
onMounted(() => root.classList.remove("dark"));
onUnmounted(() => root.classList.toggle("dark", wasDark));

const print = () => window.print();
</script>

<template>
  <div
    class="bg-border-subtle min-h-0 grow overflow-y-auto py-8 print:overflow-visible print:bg-white print:p-0"
  >
    <header class="mx-auto mb-6 flex w-[210mm] justify-between gap-4 print:hidden">
      <Button
        as-child
        variant="ghost"
      >
        <RouterLink :to="{ name: 'thrs/documentation', params: { module: route.params.module } }">
          <RiArrowLeftLine />
          {{ t("back") }}
        </RouterLink>
      </Button>
      <Button @click="print">
        <RiPrinterLine />
        {{ t("print") }}
      </Button>
    </header>
    <!-- One A4 sheet, inside the 18 mm margins the crew PDF is printed with. -->
    <div
      class="mx-auto min-h-[297mm] w-[210mm] bg-white p-[18mm] shadow-lg print:min-h-0 print:w-auto print:p-0 print:shadow-none"
    >
      <ManualDocument
        v-if="html"
        :html="html"
        printed
        class="stamped"
      />
    </div>
  </div>
</template>

<style>
@page {
  size: A4;
  margin: 18mm;
}
</style>
