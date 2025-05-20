<script setup lang="ts">
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useRoomStore } from "@/stores/rooms";
import { useDark, useTimeoutFn } from "@vueuse/core";
import { computed, inject, toRefs, watch } from "vue";

import { useI18n } from "vue-i18n";
const { toggleAmplifier } = useRoomStore();
const { currentRoom } = toRefs(useRoomStore());
const isDark = useDark();

const { t } = useI18n();

const isOn = computed({
  get: () => currentRoom.value.amplifierOn,
  set: (val) => {
    currentRoom.value.amplifierOn = val;
    toggleAmplifier(val);
  },
});

watch(currentRoom, (newRoom) => {
  useTimeoutFn(() => (isDark.value = !!newRoom.amplifierOn), 500);
});

const disabled = inject<boolean>("disabled");
</script>

<template>
  <div class="flex items-center space-x-3 text-sm">
    <Label
      for="av-toggle"
      class="font-light"
    >
      {{ t("labels.audioSystem") }}
    </Label>
    <Switch
      id="av-toggle"
      v-model:checked="isOn"
      :disabled="disabled"
      data-testid="av-toggle"
    >
    </Switch>
  </div>
</template>
