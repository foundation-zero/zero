<template>
  <div class="flex items-center">
    <div class="w-1/4 items-center justify-start">
      <slot name="left"> </slot>
    </div>

    <div class="flex w-1/2 items-center justify-center">
      <slot name="center"></slot>
    </div>

    <div class="flex w-1/4 items-center justify-end">
      <slot name="right"></slot>
    </div>
  </div>
</template>
