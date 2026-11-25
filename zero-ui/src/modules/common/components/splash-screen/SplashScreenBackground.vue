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
  background: radial-gradient(
    80.6% 62.5% at 50% 54%,
    var(--brand),
    var(--brand-muted) 50%,
    var(--brand-dull)
  );
  opacity: 0.2;
}

/* Both grids share one whole-pixel anchor at the glow centre so every major line lands on a minor line. */
.grid-lines {
  --major: color-mix(in srgb, var(--brand) var(--splash-grid-major), transparent);
  --minor: color-mix(in srgb, var(--brand) var(--splash-grid-minor), transparent);
  background-image:
    linear-gradient(to right, var(--major) 1px, transparent 1px),
    linear-gradient(to bottom, var(--major) 1px, transparent 1px),
    linear-gradient(to right, var(--minor) 1px, transparent 1px),
    linear-gradient(to bottom, var(--minor) 1px, transparent 1px);
  background-size:
    120px 120px,
    120px 120px,
    24px 24px,
    24px 24px;
  background-position: round(50vw, 1px) round(54vh, 1px);
  mask-image: radial-gradient(
    70.7% 70.7% at 50% 54%,
    rgb(0 0 0 / 0.55) 0%,
    rgb(0 0 0 / 0.62) 30%,
    #000 62%,
    rgb(0 0 0 / 0.7) 92%,
    rgb(0 0 0 / 0.4) 100%
  );
}

.vignette {
  background: radial-gradient(70.7% 70.7% at 50% 54%, transparent 60%, var(--splash-vignette) 100%);
}
</style>
