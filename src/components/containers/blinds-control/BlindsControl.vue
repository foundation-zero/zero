<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import { useUIStore } from "@/stores/ui";
import { computed, defineAsyncComponent, ref, toRefs, watch } from "vue";

const group = defineModel<BlindsGroup>("group");
const { breakpoints } = toRefs(useUIStore());

const drawer = defineAsyncComponent(() => import("./BlindsControlDrawer.vue"));
const dialog = defineAsyncComponent(() => import("./BlindsControlDialog.vue"));

const wrapper = computed(() => (breakpoints.value.phone ? drawer : dialog));
const _open = ref(false);
const open = computed<boolean>({
  get() {
    return _open.value;
  },
  set(val) {
    _open.value = val;
    if (!val) {
      setTimeout(() => (group.value = undefined), 500);
    }
  },
});

watch(group, (val) => {
  if (val) {
    _open.value = true;
  }
});
</script>

<template>
  <wrapper
    v-if="group"
    v-model:open="open"
    :group="group"
  />
</template>
