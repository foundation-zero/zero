<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Textarea } from "@/components/ui/textarea";
import { tScoped } from "@/modules/common/lib/utils";
import { ANNOTATION_COLORS, ANNOTATION_KINDS } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  AnnotationKind,
  MonitoringAnnotation,
} from "@/modules/thrapp/monitoring/monitoring.types";
import { RiChatNewLine } from "@remixicon/vue";
import { format } from "date-fns";
import { computed, ref, watch } from "vue";

/**
 * Add a note at a moment, and pick which kinds of annotations the timelines
 * show: the crew's notes, parameter changes and alarms.
 */
const props = defineProps<{
  annotations: MonitoringAnnotation[];
  /** Where a new note goes unless changed: now, or the end of a past range. */
  defaultTime: number;
  saving?: boolean;
  error?: string;
}>();

const shown = defineModel<AnnotationKind[]>("shown", { required: true });
const author = defineModel<string>("author", { required: true });
const emit = defineEmits<{ add: [annotation: { time: number; text: string }] }>();

const t = tScoped("thrapp.monitoring.annotations");
const INPUT_FORMAT = "yyyy-MM-dd'T'HH:mm";

const open = ref(false);
const timeText = ref("");
const note = ref("");
const invalid = ref(false);

watch(open, (isOpen) => {
  if (!isOpen) return;
  timeText.value = format(props.defaultTime, INPUT_FORMAT);
  note.value = "";
  invalid.value = false;
});
// Close once the note is saved.
watch(
  () => props.saving,
  (saving, wasSaving) => {
    if (wasSaving && !saving && !props.error) open.value = false;
  },
);

const counts = computed(() =>
  Object.fromEntries(
    ANNOTATION_KINDS.map((kind) => [
      kind,
      props.annotations.filter((annotation) => annotation.kind === kind).length,
    ]),
  ),
);

const toggle = (kind: AnnotationKind) => {
  shown.value = shown.value.includes(kind)
    ? shown.value.filter((each) => each !== kind)
    : [...shown.value, kind];
};

const save = () => {
  const time = Date.parse(timeText.value);
  invalid.value = !note.value.trim() || !Number.isFinite(time);
  if (!invalid.value) emit("add", { time, text: note.value });
};
</script>

<template>
  <div class="font-ui flex flex-wrap items-center gap-2 text-sm font-medium">
    <span class="text-muted-foreground mr-1">{{ t("show") }}</span>
    <button
      v-for="kind in ANNOTATION_KINDS"
      :key="kind"
      type="button"
      class="border-border-subtle flex h-8 items-center gap-2 rounded-full border px-3 transition-colors"
      :class="
        shown.includes(kind)
          ? 'bg-background text-foreground'
          : 'text-muted-foreground bg-transparent opacity-70'
      "
      :aria-pressed="shown.includes(kind)"
      @click="toggle(kind)"
    >
      <span
        class="size-2.5 rounded-full"
        :style="{ backgroundColor: ANNOTATION_COLORS[kind] }"
        aria-hidden="true"
      />
      {{ t(`kinds.${kind}`) }}
      <span class="text-muted-foreground tabular-nums">{{ counts[kind] }}</span>
    </button>

    <Popover v-model:open="open">
      <PopoverTrigger as-child>
        <Button
          variant="secondary"
          size="sm"
          class="ml-1 h-8"
        >
          <RiChatNewLine />
          {{ t("add") }}
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="end"
        class="font-ui w-80"
      >
        <form
          class="flex flex-col gap-3"
          @submit.prevent="save"
        >
          <h4 class="text-popover-foreground text-sm font-semibold">{{ t("add") }}</h4>
          <label class="text-popover-foreground/70 flex flex-col gap-1 text-sm font-medium">
            {{ t("time") }}
            <Input
              v-model="timeText"
              type="datetime-local"
              step="60"
            />
          </label>
          <label class="text-popover-foreground/70 flex flex-col gap-1 text-sm font-medium">
            {{ t("note") }}
            <Textarea
              v-model="note"
              rows="3"
              maxlength="500"
              :placeholder="t('notePlaceholder')"
              :aria-invalid="invalid"
            />
          </label>
          <label class="text-popover-foreground/70 flex flex-col gap-1 text-sm font-medium">
            {{ t("author") }}
            <Input
              v-model="author"
              maxlength="80"
              :placeholder="t('authorPlaceholder')"
            />
          </label>
          <p
            v-if="invalid || props.error"
            class="text-destructive text-xs"
          >
            {{ invalid ? t("noteRequired") : props.error }}
          </p>
          <Button
            type="submit"
            size="sm"
            class="self-start"
            :disabled="props.saving"
          >
            {{ t("save") }}
          </Button>
        </form>
      </PopoverContent>
    </Popover>
  </div>
</template>
