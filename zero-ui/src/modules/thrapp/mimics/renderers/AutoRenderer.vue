<script setup lang="ts">
import { ControllerFields, ControlValueFields, SensorValueFields } from "@/modules/thrsim/types";
import { computed } from "vue";
import { FieldRenderer } from ".";
import { injectFieldValueField, injectFieldValueSource, isPlaceholderField } from "../providers";

const field = injectFieldValueField<ControlValueFields | SensorValueFields | ControllerFields>();
const source = injectFieldValueSource();

const editor = computed(() => {
  if (!field) return null;
  else if (isPlaceholderField(source)) {
    return FieldRenderer.Placeholder;
  } else {
    switch (field) {
      case "temperature":
      case "temperatureSetpoint":
        return FieldRenderer.Temperature;
      case "on":
        return FieldRenderer.OnOff;
      case "deltaT":
        return FieldRenderer.DeltaT;
      case "empty":
        return FieldRenderer.Empty;
      case "flow":
        return FieldRenderer.FlowRate;
      case "setpoint":
        return FieldRenderer.ValveState;
      case "positionAbs":
        return FieldRenderer.Degree;
      case "positionRel":
      case "dutypoint":
        return FieldRenderer.Percentage;
      case "heat":
        return FieldRenderer.Heat;
      case "level":
        return FieldRenderer.Level;
      case "quantity":
        return FieldRenderer.QuantityLiters;
      case "speed":
        return FieldRenderer.Frequency;
      case "opTime":
        return FieldRenderer.TimeRemaining;
      case "pressure":
        return FieldRenderer.Pressure;
      case "timeToFill":
        return FieldRenderer.TimeRemaining;
      case "tank1State":
      case "tank2State":
      case "tank3State":
        return FieldRenderer.BoilerTankMode;
    }

    return null;
  }
});
</script>

<template>
  <component
    :is="editor"
    v-if="editor"
    v-bind="$props"
  >
    <slot />
  </component>
</template>
