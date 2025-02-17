<script setup lang="ts">
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { computed } from "vue";
import { LightsSlider } from "../lights-slider";
import { ListItem } from "../list";
import { ZSpacer } from "../spacer";
import { Switch } from "../switch";

defineProps<{ name: string }>();
const level = defineModel<number>("level", { required: true });

const on = computed({
  get() {
    return level.value! > 0;
  },
  set(val: boolean) {
    level.value = val ? 100 : 0;
  },
});
</script>
<template>
  <ListItem class="flex-col space-y-3 py-6">
    <span class="flex w-full items-center">
      <LampCeiling
        v-if="name === 'Ambient'"
        class="mr-3 inline"
        :size="18"
      />
      <LampWallUp
        v-else
        class="mr-3 inline"
        :size="18"
      />
      <span class="text-md font-medium"> {{ name }}</span>
      <ZSpacer />
      <Switch v-model:checked="on"></Switch>
    </span>

    <LightsSlider
      v-model:brightness="level"
      :on="on"
    />
  </ListItem>
</template>
