<script setup lang="ts">
import { LightingControl } from "@/@types";
import { Switch } from "@/components/ui/shadcn/switch";
import { ListItem } from "@/components/ui/shared/list";
import { ratioAsPercentage } from "@/lib/utils";
import { LightsSlider } from "@components/shared/lights-slider";
import { ZSpacer } from "@components/shared/spacer";
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { computed, inject, Ref, ref, toRef, watch } from "vue";
import { getContext } from ".";

const props = defineProps<{ control: LightingControl }>();
const control = toRef(props, "control");
const brightness = ref(control.value.value);

const context = getContext();

watch(
  control,
  (control) => {
    brightness.value = control.value;
  },
  { immediate: true },
);

const brightnessPercentage = ratioAsPercentage(brightness);
const disabled = inject<Ref<boolean>>("disabled", ref(false));

const on = computed({
  get() {
    return brightness.value! > 0;
  },
  set(val: boolean) {
    brightness.value = val ? 1 : 0;
    commit();
  },
});

const commit = () => context.commit(props.control, brightness);
</script>
<template>
  <ListItem class="flex-col space-y-3 py-6">
    <span class="flex w-full items-center">
      <LampCeiling
        v-if="control.name === 'Ambient'"
        class="mr-3 inline"
        :size="18"
      />
      <LampWallUp
        v-else
        class="mr-3 inline"
        :size="18"
      />
      <label class="text-md text-muted-foreground font-medium"> {{ control.name }}</label>
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
      @click="commit()"
      @touchend="commit()"
    />
  </ListItem>
</template>
