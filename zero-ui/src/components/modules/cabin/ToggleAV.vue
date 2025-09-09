<script setup lang="ts">
import { Label } from "@/components/ui/shadcn/label";
import { Switch } from "@/components/ui/shadcn/switch";
import { extractAmplifierStatus, isAmplifierControl } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { computed, inject, toRefs } from "vue";

import { useI18n } from "vue-i18n";
const { toggleAmplifier } = useRoomStore();
const { currentRoom } = toRefs(useRoomStore());

const { t } = useI18n();

const amplifierStatus = computed(() => extractAmplifierStatus(currentRoom.value));

const isOn = computed({
  get: () => amplifierStatus.value === 1,
  set: (val) => {
    const amp = currentRoom.value.roomsControls.find(isAmplifierControl);

    if (!amp) return;

    toggleAmplifier(val, amp);

    amp.value = val ? 1 : 0;
  },
});

const disabled = inject<boolean>("disabled");
</script>

<template>
  <div
    v-if="amplifierStatus !== undefined"
    class="flex items-center space-x-3 text-sm"
  >
    <Label
      for="av-toggle"
      class="font-light"
    >
      {{ t("labels.audioSystem") }}
    </Label>
    <Switch
      id="av-toggle"
      v-model="isOn"
      :disabled="disabled"
      data-testid="av-toggle"
    >
    </Switch>
  </div>
</template>
