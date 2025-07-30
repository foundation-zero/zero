<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import { useUIStore } from "@/stores/ui";
import { ResponsivePopup } from "@components/shared/responsive-dialog";
import { useTimeoutFn } from "@vueuse/core";
import { computed, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import BlindsList from "./BlindsList.vue";

const group = defineModel<BlindsGroup>("group");

const { t } = useI18n();

const { breakpoints } = toRefs(useUIStore());
const _open = ref(false);
const open = computed<boolean>({
  get() {
    return _open.value;
  },
  set(val) {
    _open.value = val;
    useTimeoutFn(() => (group.value = undefined), 500);
  },
});

watch(group, (val) => {
  if (val) {
    _open.value = true;
  }
});
</script>

<template>
  <ResponsivePopup
    v-if="group"
    v-model:open="open"
    :title="group.name"
    :description="t('views.blinds.description')"
  >
    <BlindsList
      :group="group"
      :class="{ 'mx-3 mb-3': breakpoints.phone, 'w-full': !breakpoints.phone }"
    />
  </ResponsivePopup>
</template>
