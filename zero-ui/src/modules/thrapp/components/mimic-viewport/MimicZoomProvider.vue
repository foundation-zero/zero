<script setup lang="ts">
import { createMimicZoomContext, provideMimicZoomContext } from "./context";

// Shares the zoom state between a `MimicViewport` and its `ZoomControls`, wherever they are placed
// inside this provider.
provideMimicZoomContext(createMimicZoomContext());
</script>

<template>
  <slot />
</template>
