<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { LightingControl } from "@/modules/domestic/types";
import { LightsSlider } from "@common/components/lights-slider";
import { ListItem } from "@common/components/list";
import { ZSpacer } from "@common/components/spacer";
import { ratioAsPercentage } from "@common/lib/utils";
import { RiLightbulbFill, RiLightbulbLine } from "@remixicon/vue";
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
      <RiLightbulbLine
        v-if="control.name === 'Ambient'"
        class="mr-3 inline"
        size="18"
      />
      <RiLightbulbFill
        v-else
        class="mr-3 inline"
        size="18"
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
