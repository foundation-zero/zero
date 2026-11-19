<template>
  <div
    class="pointer-events-none fixed inset-0"
    aria-hidden="true"
  >
    <div class="glow absolute inset-0" />
    <div class="grid-lines absolute inset-0" />
    <div class="vignette absolute inset-0" />
  </div>
</template>

<style scoped>
.glow {
  background: radial-gradient(62% 80% at 50% 54%, #99b6cc 0%, #779dbb 50%, #5685a9 100%);
  opacity: 0.18;
}

/* Both grids share one whole-pixel anchor at the glow centre so every major line lands on a minor line. */
.grid-lines {
  background-image:
    linear-gradient(to right, var(--splash-grid-major) 1px, transparent 1px),
    linear-gradient(to bottom, var(--splash-grid-major) 1px, transparent 1px),
    linear-gradient(to right, var(--splash-grid-minor) 1px, transparent 1px),
    linear-gradient(to bottom, var(--splash-grid-minor) 1px, transparent 1px);
  background-size:
    120px 120px,
    120px 120px,
    24px 24px,
    24px 24px;
  background-position: round(50vw, 1px) round(54vh, 1px);
  mask-image: radial-gradient(
    farthest-corner at 50% 54%,
    rgb(0 0 0 / 0.55) 0%,
    rgb(0 0 0 / 0.62) 30%,
    #000 62%,
    rgb(0 0 0 / 0.7) 92%,
    rgb(0 0 0 / 0.4) 100%
  );
}

.vignette {
  background: radial-gradient(
    farthest-corner at 50% 54%,
    transparent 60%,
    var(--splash-vignette) 100%
  );
}
</style>
