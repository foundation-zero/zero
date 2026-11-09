<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group";
import { useAutomationStore } from "@/modules/thrapp/stores/automation";
import { ENV } from "@/settings";
import { RiLock2Line } from "@remixicon/vue";
import { inject, Ref } from "vue";
import { useI18n } from "vue-i18n";
import { useManualModeUnlock } from "./manual-mode-toggle.utils";

const { t } = useI18n();

const emit = defineEmits(["close"]);

const { setAutomatedControl } = useAutomationStore();
const currentDefinition = inject<Ref<string>>("currentModule")!;

const { password, isValid, confirm, cancel, remaining, isActive } = useManualModeUnlock(
  ENV.VITE_MANUAL_MODE_PWD,
  async () => {
    await setAutomatedControl(currentDefinition.value)(false);
    emit("close");
  },
);

const close = () => {
  cancel();
  emit("close");
};
</script>

<template>
  <section class="grid gap-6 max-md:px-4">
    <h2 class="text-xl font-bold">
      {{ t("thrapp.dialogs.manualMode.title") }}
    </h2>

    <p class="font-ui!">{{ t("thrapp.dialogs.manualMode.description") }}</p>

    <InputGroup>
      <InputGroupInput
        v-model="password"
        :placeholder="t('thrapp.dialogs.manualMode.password')"
        type="password"
        @keyup.enter="confirm"
      />
      <InputGroupAddon>
        <RiLock2Line />
      </InputGroupAddon>
    </InputGroup>

    <div class="flex items-center gap-6">
      <Button
        :disabled="!isValid || isActive"
        @click="confirm"
      >
        {{ t("thrapp.dialogs.manualMode.confirm", { count: remaining }) }}
      </Button>
      <Button @click="close">
        {{ t("thrapp.dialogs.manualMode.cancel") }}
      </Button>
    </div>
  </section>
</template>
