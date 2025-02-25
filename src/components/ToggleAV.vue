<script setup lang="ts">
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useRoomStore } from "@/stores/rooms";
import { useDark } from "@vueuse/core";
import { computed, toRefs, watch } from "vue";

const { toggleAmplifier } = useRoomStore();
const { currentRoom } = toRefs(useRoomStore());
const isDark = useDark();

const isOn = computed({
  get: () => currentRoom.value.amplifierOn,
  set: (val) => {
    currentRoom.value.amplifierOn = val;
    toggleAmplifier(val);
  },
});

watch(currentRoom, (newRoom) => {
  isDark.value = !!newRoom.amplifierOn;
});
</script>

<template>
  <div class="flex items-center space-x-3 text-sm">
    <Label
      for="av-toggle"
      class="font-light"
    >
      Audio System
    </Label>
    <Switch
      id="av-toggle"
      v-model:checked="isOn"
    >
    </Switch>
  </div>
</template>
