<script
  setup
  lang="ts"
  generic="
    Type extends SensorComponentType.Temperature | SensorComponentType.Flow,
    Parameter extends ParametersType = Type extends SensorComponentType.Temperature
      ? ParametersType.Temperature
      : ParametersType.Flow | ParametersType.FlowControl
  "
>
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { computed } from "vue";
import * as Partials from ".";
import { useTranslations } from "..";
import { ControllerStateValue, ModuleField, ParameterValue } from "../../providers";
import { FieldRenderer } from "../../renderers";
const { items, sources } = useTranslations();

const props = defineProps<{
  type: Type;
  controller: ModuleField<ControllerStateComponentType.PIDController>;
  actuator?: ModuleField;
  measurement?: ModuleField<Type>;
  setpoint?: ModuleField<Parameter>;
  outputMinimum?: ModuleField<Parameter>;
}>();

const fieldRenderer = computed(() => {
  if (props.type === SensorComponentType.Temperature) {
    return FieldRenderer.Temperature;
  } else {
    return FieldRenderer.FlowRate;
  }
});
</script>

<template>
  <ControllerStateValue
    :source="controller"
    field="enabled"
  >
    <Partials.ListItem>
      <template #value>
        <FieldRenderer.HeatPumpMode />
      </template>
    </Partials.ListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="output"
  >
    <Partials.ListItem
      size="sm"
      :renderer="FieldRenderer.Percentage"
    >
      {{ items("actuator") }}
      <template #source>
        <slot name="actuator">
          <FieldRenderer.Source :source="actuator">
            <template v-if="!actuator">
              {{ sources("this") }}
            </template>
          </FieldRenderer.Source>
        </slot>
      </template>
    </Partials.ListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="setpoint"
  >
    <Partials.ListItem
      size="sm"
      :renderer="fieldRenderer"
    >
      {{ items("setpoint") }}
      <template #source>
        <slot name="setpoint">
          <FieldRenderer.Source :source="setpoint" />
        </slot>
      </template>
    </Partials.ListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="measurement"
  >
    <Partials.ListItem
      size="sm"
      :renderer="fieldRenderer"
    >
      {{ items("measurement") }}
      <template #source>
        <slot name="measurement">
          <FieldRenderer.Source :source="measurement">
            <template v-if="!measurement">
              {{ sources("this") }}
            </template>
          </FieldRenderer.Source>
        </slot>
      </template>
    </Partials.ListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="error"
  >
    <Partials.ListItem
      size="sm"
      :renderer="fieldRenderer"
    >
      {{ items("error") }}
      <template #sourceName>
        {{ sources("calculated") }}
      </template>
    </Partials.ListItem>
  </ControllerStateValue>

  <ParameterValue
    v-if="outputMinimum"
    :source="outputMinimum"
  >
    <Partials.ListItem
      size="sm"
      :renderer="FieldRenderer.Percentage"
    >
      {{ items("outputMinimum") }}
    </Partials.ListItem>
  </ParameterValue>
</template>
