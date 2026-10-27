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
import { tScoped } from "@/modules/common/lib/utils";
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";
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
  target?: ModuleField<Parameter>;
  outputMinimum?: ModuleField<Parameter>;
}>();

const fieldRenderer = computed(() => {
  if (props.type === SensorComponentType.Temperature) {
    return FieldRenderer.Temperature;
  } else {
    return FieldRenderer.FlowRate;
  }
});

const t = tScoped("thrapp.parameters.pid");
</script>

<template>
  <slot name="header">
    <ControllerStateValue
      :source="controller"
      field="enabled"
    >
      <Partials.ListItem>
        <template #source>
          <FieldRenderer.Source
            :source="controller"
            class="text-foreground"
          >
            {{ t(`${controller[2]}.title`) }}
          </FieldRenderer.Source>
        </template>
        <template #value>
          <FieldRenderer.HeatPumpMode />
        </template>
      </Partials.ListItem>
    </ControllerStateValue>
  </slot>

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
          <FieldRenderer.Source
            :source="actuator"
            api-only
          />
        </slot>
      </template>
    </Partials.ListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="target"
  >
    <Partials.ListItem
      size="sm"
      :renderer="fieldRenderer"
      :no-source="!target"
    >
      {{ items("target") }}
      <template #source>
        <slot name="target">
          <FieldRenderer.Source
            v-if="target"
            :source="target"
          />
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
          <FieldRenderer.Source
            :source="measurement"
            api-only
          />
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
