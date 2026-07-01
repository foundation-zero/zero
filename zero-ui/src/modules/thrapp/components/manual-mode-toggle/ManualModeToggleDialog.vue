<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group";
import { RiLock2Line } from "@remixicon/vue";
import { useCountdown } from "@vueuse/core";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useAutomaticMode } from "../../state";

const { t } = useI18n();

const emit = defineEmits(["close"]);

const cancel = () => {
  if (!isActive.value) {
    emit("close");
  }

  stop();
};

const COOLDOWN_SECONDS = 10;
const MATCH_PASSWORD = "zerosecurity";
const password = ref("");

const automaticMode = useAutomaticMode();

const { stop, start, remaining, isActive } = useCountdown(COOLDOWN_SECONDS, {
  immediate: false,
  onComplete: async () => {
    automaticMode.value = false;
    cancel();
  },
});
</script>

<template>
  <section class="grid gap-6 max-md:px-4">
    <h2 class="text-xl font-medium">
      {{ t("thrapp.dialogs.manualMode.title") }}
    </h2>

    <header class="font-ui!">{{ t("thrapp.dialogs.manualMode.description") }}</header>

    <InputGroup>
      <InputGroupInput
        v-model="password"
        :placeholder="t('thrapp.dialogs.manualMode.password')"
        type="password"
      />
      <InputGroupAddon>
        <RiLock2Line />
      </InputGroupAddon>
    </InputGroup>

    <div class="flex items-center gap-6">
      <Button
        :disabled="password !== MATCH_PASSWORD || isActive"
        @click="() => start()"
        >{{ t("thrapp.dialogs.manualMode.confirm") }}</Button
      >
      <Button @click="cancel">
        {{ t("thrapp.dialogs.manualMode.cancel", { count: isActive ? remaining : 0 }) }}
      </Button>
    </div>
  </section>
</template>
