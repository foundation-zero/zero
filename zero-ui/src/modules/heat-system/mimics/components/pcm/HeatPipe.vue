<script setup lang="ts">
withDefaults(defineProps<{ orientation?: "left" | "right" }>(), {
  orientation: "left",
});
</script>

<template>
  <svg
    width="41"
    height="62"
    viewBox="0 0 41 62"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g :transform="orientation === 'right' ? 'translate(41 0) scale(-1 1)' : undefined">
      <path
        d="M14.7679 20.54C9.2451 20.54 4.76794 25.0172 4.76794 30.54C4.76794 36.0629 9.2451 40.54 14.7679 40.54"
        class="stroke-flows-connecting"
      />
      <path
        d="M29.7675 20.5433C35.2903 20.5433 39.7675 16.0662 39.7675 10.5433C39.7675 5.02049 35.2903 0.543335 29.7675 0.543335"
        class="stroke-flows-connecting"
      />
      <path
        d="M29.7675 60.5927C35.2903 60.5927 39.7675 56.1155 39.7675 50.5927C39.7675 45.0698 35.2903 40.5927 29.7675 40.5927"
        class="stroke-flows-connecting"
      />
      <line
        x1="29.7672"
        y1="20.5408"
        x2="14.7672"
        y2="20.5408"
        class="stroke-flows-connecting"
      />
      <line
        x1="29.7673"
        y1="60.5906"
        x2="14.7673"
        y2="60.5906"
        class="stroke-flows-connecting"
      />
      <line
        x1="15.2039"
        y1="60.5906"
        x2="6.09914e-05"
        y2="60.5906"
        class="stroke-flows-connecting"
      />
      <line
        x1="29.7672"
        y1="0.5"
        x2="14.7672"
        y2="0.499999"
        class="stroke-flows-connecting"
      />
      <line
        x1="14.8624"
        y1="0.5"
        x2="0.00299068"
        y2="0.499999"
        class="stroke-flows-connecting"
      />
      <line
        x1="29.7672"
        y1="40.5814"
        x2="14.7672"
        y2="40.5814"
        class="stroke-flows-connecting"
      />
    </g>
  </svg>
</template>
