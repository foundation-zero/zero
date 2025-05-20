<script setup lang="ts">
import { LightingGroups } from "@/gql/graphql";
import { ratioAsPercentage } from "@/lib/utils";
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { computed, inject, ref, toRef, watch } from "vue";
import { LightsSlider } from "../lights-slider";
import { ListItem } from "../list";
import { ZSpacer } from "../spacer";
import { Switch } from "../switch";

const props = defineProps<{ light: LightingGroups }>();
const brightness = ref(props.light.level);

watch(
  toRef(props, "light"),
  (light) => {
    brightness.value = light.level;
  },
  { immediate: true },
);

const emit = defineEmits<{
  "update:level": [number];
}>();

const brightnessPercentage = ratioAsPercentage(brightness);
const disabled = inject<boolean>("disabled");

const on = computed({
  get() {
    return brightness.value! > 0;
  },
  set(val: boolean) {
    brightness.value = val ? 1 : 0;
    emit("update:level", val ? 1 : 0);
  },
});
</script>
<template>
  <ListItem class="flex-col space-y-3 py-6">
    <span class="flex w-full items-center">
      <LampCeiling
        v-if="light.name === 'Ambient'"
        class="mr-3 inline"
        :size="18"
      />
      <LampWallUp
        v-else
        class="mr-3 inline"
        :size="18"
      />
      <span class="text-md font-medium"> {{ light.name }}</span>
      <ZSpacer />
      <Switch
        v-model:checked="on"
        :disabled="disabled"
      ></Switch>
    </span>

    <LightsSlider
      v-model:brightness="brightnessPercentage"
      :on="on"
      :disabled="disabled"
      @click="emit('update:level', brightness)"
      @touchend="emit('update:level', brightness)"
    />
  </ListItem>
</template>
