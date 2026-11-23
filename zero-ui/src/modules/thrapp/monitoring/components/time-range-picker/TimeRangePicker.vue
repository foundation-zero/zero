<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
import { tScoped } from "@/modules/common/lib/utils";
import { RANGE_PRESETS, REFRESH_INTERVALS } from "@/modules/thrapp/monitoring/monitoring.consts";
import type { TimeRange } from "@/modules/thrapp/monitoring/monitoring.types";
import {
  customRange,
  isLive,
  presetKey,
  resolveRange,
  shiftRange,
  zoomOut,
} from "@/modules/thrapp/monitoring/monitoring.utils";
import {
  RiArrowDownSLine,
  RiArrowLeftDoubleLine,
  RiArrowRightDoubleLine,
  RiRefreshLine,
  RiTimeLine,
  RiZoomOutLine,
} from "@remixicon/vue";
import { format } from "date-fns";
import { computed, ref, watch } from "vue";

/**
 * « / » shift the window by one period, the centre opens quick ranges and a
 * custom from / to, and the
 * magnifier doubles the range. Refresh reloads; its chevron sets auto-refresh.
 */
const range = defineModel<TimeRange>({ required: true });
const interval = defineModel<number>("interval", { required: true });
const emit = defineEmits<{ refresh: [] }>();

const t = tScoped("thrapp.monitoring.timeRange");

const label = computed(() => {
  const key = presetKey(range.value.span);
  if (key && isLive(range.value)) return t(`presets.${key}`);
  const { start, end } = resolveRange(range.value, Date.now());
  return t("custom", { start: format(start, "dd MMM HH:mm"), end: format(end, "dd MMM HH:mm") });
});

const preset = computed(() => (isLive(range.value) ? presetKey(range.value.span) : undefined));

const open = ref(false);
const fromText = ref("");
const toText = ref("");
const customError = ref<string | null>(null);
const INPUT_FORMAT = "yyyy-MM-dd'T'HH:mm";

// Opening the popover fills in the range shown now.
watch(open, (isOpen) => {
  if (!isOpen) return;
  const { start, end } = resolveRange(range.value, Date.now());
  fromText.value = format(start, INPUT_FORMAT);
  toText.value = format(end, INPUT_FORMAT);
  customError.value = null;
});

const choosePreset = (span: number) => {
  range.value = { span, end: null };
  open.value = false;
};
const applyCustom = () => {
  const result = customRange(Date.parse(fromText.value), Date.parse(toText.value), Date.now());
  if ("error" in result) {
    customError.value = result.error;
    return;
  }
  range.value = result.range;
  open.value = false;
};

const intervalValue = computed({
  get: () => String(interval.value),
  set: (value: string) => (interval.value = Number(value)),
});

const segment = "flex h-full items-center px-2 hover:bg-background/40 disabled:opacity-40";
</script>

<template>
  <div
    class="font-ui text-muted-foreground flex flex-wrap items-center gap-2 text-base font-medium"
    role="toolbar"
    :aria-label="t('label')"
  >
    <div
      class="bg-muted border-border-subtle divide-border-subtle flex h-9 items-center divide-x overflow-hidden rounded-lg border"
    >
      <button
        type="button"
        :class="segment"
        :title="t('previous')"
        :aria-label="t('previous')"
        @click="range = shiftRange(range, -1, Date.now())"
      >
        <RiArrowLeftDoubleLine class="size-5" />
      </button>
      <Popover v-model:open="open">
        <PopoverTrigger
          class="hover:bg-background/40 flex h-full items-center gap-2 px-3"
          :aria-label="t('label')"
        >
          <RiTimeLine class="size-5" />
          {{ label }}
          <RiArrowDownSLine class="size-4 opacity-60" />
        </PopoverTrigger>
        <PopoverContent
          align="end"
          class="font-ui flex w-auto gap-6 p-4 max-sm:flex-col"
        >
          <form
            class="flex w-64 flex-col gap-3"
            @submit.prevent="applyCustom"
          >
            <h4 class="text-popover-foreground text-sm font-semibold">{{ t("customTitle") }}</h4>
            <label class="text-popover-foreground/70 flex flex-col gap-1 text-sm font-medium">
              {{ t("from") }}
              <Input
                v-model="fromText"
                type="datetime-local"
                step="60"
                :invalid="!!customError"
              />
            </label>
            <label class="text-popover-foreground/70 flex flex-col gap-1 text-sm font-medium">
              {{ t("to") }}
              <Input
                v-model="toText"
                type="datetime-local"
                step="60"
                :invalid="!!customError"
              />
            </label>
            <p
              v-if="customError"
              class="text-destructive text-xs"
            >
              {{ t(`errors.${customError}`) }}
            </p>
            <Button
              type="submit"
              size="sm"
              class="self-start"
            >
              {{ t("apply") }}
            </Button>
          </form>
          <div class="border-popover-foreground/20 flex flex-col gap-1 sm:border-l sm:pl-6">
            <h4 class="text-popover-foreground mb-2 text-sm font-semibold">
              {{ t("quickRanges") }}
            </h4>
            <button
              v-for="option in RANGE_PRESETS"
              :key="option.key"
              type="button"
              class="hover:bg-popover-foreground/10 text-popover-foreground rounded-xs px-2 py-1 text-left text-sm"
              :class="preset === option.key ? 'font-semibold' : 'opacity-75'"
              @click="choosePreset(option.span)"
            >
              {{ t(`presets.${option.key}`) }}
            </button>
          </div>
        </PopoverContent>
      </Popover>
      <button
        type="button"
        :class="segment"
        :title="t('next')"
        :aria-label="t('next')"
        :disabled="isLive(range)"
        @click="range = shiftRange(range, 1, Date.now())"
      >
        <RiArrowRightDoubleLine class="size-5" />
      </button>
      <button
        type="button"
        :class="segment"
        :title="t('zoomOut')"
        :aria-label="t('zoomOut')"
        @click="range = zoomOut(range)"
      >
        <RiZoomOutLine class="size-5" />
      </button>
    </div>

    <div
      class="bg-muted border-border-subtle divide-border-subtle flex h-9 items-center divide-x overflow-hidden rounded-lg border"
    >
      <button
        type="button"
        :class="[segment, 'gap-2 px-3']"
        @click="emit('refresh')"
      >
        <RiRefreshLine class="size-5" />
        {{ t("refresh") }}
      </button>
      <Select v-model="intervalValue">
        <SelectTrigger
          class="h-full rounded-none border-0 bg-transparent px-2 shadow-none dark:bg-transparent"
          :aria-label="t('autoRefresh')"
          :title="t(`intervals.${interval}`)"
        >
          <span
            v-if="interval"
            class="text-xs"
          >
            {{ t(`intervals.${interval}`) }}
          </span>
        </SelectTrigger>
        <SelectContent>
          <SelectItem
            v-for="option in REFRESH_INTERVALS"
            :key="option"
            :value="String(option)"
          >
            {{ t(`intervals.${option}`) }}
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  </div>
</template>
