import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from ".";
import NumberFieldPrefix from "./NumberFieldPrefix.vue";

const components = {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
  NumberFieldPrefix,
};

const meta = {
  title: "UI/NumberField",
  component: NumberField,
  argTypes: {
    min: { control: "number" },
    max: { control: "number" },
    step: { control: "number" },
    disabled: { control: "boolean" },
  },
  args: { min: 0, max: 100, step: 1, disabled: false },
  render: (args) => ({
    components,
    setup: () => ({ args, value: ref(60) }),
    template: `
      <NumberField v-bind="args" v-model="value" class="w-[200px]">
        <NumberFieldContent>
          <NumberFieldDecrement />
          <NumberFieldInput />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>`,
  }),
} satisfies Meta<typeof NumberField>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Disabled: Story = { args: { disabled: true } };

export const WithPrefix: Story = {
  render: (args) => ({
    components,
    setup: () => ({ args, value: ref(45) }),
    template: `
      <NumberField v-bind="args" v-model="value" class="w-[220px]">
        <NumberFieldContent>
          <NumberFieldPrefix>°C</NumberFieldPrefix>
          <NumberFieldInput />
        </NumberFieldContent>
      </NumberField>`,
  }),
};
