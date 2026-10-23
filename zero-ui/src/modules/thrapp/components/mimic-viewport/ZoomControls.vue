<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { tScoped } from "@/modules/common/lib/utils";
import { RiSearch2Line, RiZoomInLine, RiZoomOutLine } from "@remixicon/vue";

defineProps<{ canZoomIn: boolean; canZoomOut: boolean }>();
const emit = defineEmits<{ zoomIn: []; zoomOut: []; actualSize: []; fit: [] }>();

const t = tScoped("thrapp.labels.zoom");
</script>

<template>
  <div
    class="flex [&>button]:rounded-none [&>button]:first:rounded-l-lg [&>button]:last:rounded-r-lg [&>button:not(:first-child)]:-ml-px"
    role="group"
    :aria-label="t('controls')"
  >
    <Button
      variant="secondary"
      size="icon"
      :disabled="!canZoomIn"
      :title="t('in')"
      :aria-label="t('in')"
      @click="emit('zoomIn')"
    >
      <RiZoomInLine class="size-5" />
    </Button>
    <Button
      variant="secondary"
      size="icon"
      :title="t('actualSize')"
      :aria-label="t('actualSize')"
      @click="emit('actualSize')"
    >
      <span class="relative size-5">
        <RiSearch2Line class="size-5" />
        <!-- "1" inside the magnifier lens, as in the design. -->
        <span
          class="absolute top-[9px] left-[7px] w-1.5 -translate-y-1/2 text-center text-[10px] leading-none"
          aria-hidden="true"
        >
          1
        </span>
      </span>
    </Button>
    <Button
      variant="secondary"
      size="icon"
      :title="t('fit')"
      :aria-label="t('fit')"
      @click="emit('fit')"
    >
      <span class="relative size-5">
        <RiSearch2Line class="size-5" />
        <!-- Diagonal expand arrows inside the magnifier lens, as in the design. -->
        <svg
          class="absolute top-1.5 left-1.5 size-1.5"
          viewBox="0 0 6 6"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            d="M4.86193 0.666667H3.66667V0H6V2.33333H5.33333V1.13807L3.90237 2.56903L3.43097 2.09763L4.86193 0.666667ZM0 3.66667H0.666667V4.86193L2.09763 3.43097L2.56903 3.90237L1.13807 5.33333H2.33333V6H0V3.66667Z"
          />
        </svg>
      </span>
    </Button>
    <Button
      variant="secondary"
      size="icon"
      :disabled="!canZoomOut"
      :title="t('out')"
      :aria-label="t('out')"
      @click="emit('zoomOut')"
    >
      <RiZoomOutLine class="size-5" />
    </Button>
  </div>
</template>
