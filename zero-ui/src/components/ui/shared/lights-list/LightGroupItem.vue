<script setup lang="ts">
import { LightingControl } from "@/@types";
import { Switch } from "@/components/ui/shadcn/switch";
import { ListItem } from "@/components/ui/shared/list";
import { ratioAsPercentage } from "@/lib/utils";
import { LightsSlider } from "@components/shared/lights-slider";
import { ZSpacer } from "@components/shared/spacer";
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { computed, inject, ref, toRef, watch } from "vue";

const props = defineProps<{ light: LightingControl }>();
const brightness = ref(props.light.value);

watch(
  toRef(props, "light"),
  (light) => {
    brightness.value = light.value;
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
        v-model="on"
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
