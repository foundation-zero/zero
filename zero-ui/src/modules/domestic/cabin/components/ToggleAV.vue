<script setup lang="ts">
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { extractAmplifierStatus, isAmplifierControl } from "@common/lib/utils";
import { computed, toRefs } from "vue";

import { useI18n } from "vue-i18n";
const { toggleAmplifier } = useRoomStore();
const { currentRoom, hasPendingRequests } = toRefs(useRoomStore());

const { t } = useI18n();

const amplifierStatus = computed(() => extractAmplifierStatus(currentRoom.value));

const isOn = computed({
  get: () => amplifierStatus.value === 1,
  set: (val) => {
    const amp = currentRoom.value.roomControls.find(isAmplifierControl);

    if (!amp) return;

    toggleAmplifier(val, currentRoom.value.id);

    amp.value = val ? 1 : 0;
  },
});
</script>

<template>
  <div class="flex items-center space-x-3 text-sm">
    <Label
      for="av-toggle"
      class="text-xs font-light md:text-sm!"
    >
      {{ t("labels.audioSystem") }}
    </Label>
    <Switch
      id="av-toggle"
      v-model="isOn"
      :disabled="hasPendingRequests"
      data-testid="av-toggle"
    >
    </Switch>
  </div>
</template>
