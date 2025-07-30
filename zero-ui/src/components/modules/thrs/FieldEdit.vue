<script lang="ts" setup generic="T extends 'number' | 'boolean' | 'string'">
import { Field, TypeToType } from "@/stores/thrs";
import { Checkbox } from "@components/shadcn/checkbox";
import { Label } from "@components/shadcn/label";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@components/shadcn/number-field";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@components/shadcn/select";
import { computed } from "vue";

const props = defineProps<{
  field: Field<T>;
  disabled?: boolean;
}>();
const model = defineModel<object>({ required: true });
const value = computed<TypeToType<T> | undefined>({
  get: () => props.field.get(model.value) ?? props.field.default,
  set: (v: TypeToType<T> | undefined) => {
    if (v !== undefined) {
      model.value = props.field.set(model.value, v);
    }
  },
});
</script>
<template>
  <div>
    <NumberField
      v-if="field.type === 'number'"
      :id="field.name"
      v-model="
        value as number // should be safe by generic
      "
      :default-value="18"
      :min="field.minimum"
      :max="field.maximum"
    >
      <Label :for="field.name">{{ field.name }}</Label>
      <NumberFieldContent>
        <NumberFieldDecrement />
        <NumberFieldInput />
        <NumberFieldIncrement />
      </NumberFieldContent>
    </NumberField>
    <div v-else-if="field.type === 'boolean'">
      <Checkbox
        :id="field.name"
        v-model:checked="
          value as boolean // should be safe by generic
        "
      />
      <Label :for="field.name">
        {{ field.name }}
      </Label>
    </div>
    <div v-else-if="field.type === 'string'">
      <Label :for="field.name">{{ field.name }}</Label>
      <Select
        :id="field.name"
        v-model="
          value as string // should be safe by generic
        "
      >
        <SelectTrigger>
          <SelectValue :placeholder="field.name" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectItem
              v-for="item in field.items"
              :key="item"
              :value="item"
            >
              {{ item }}
            </SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  </div>
</template>
