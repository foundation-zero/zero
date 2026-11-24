import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { Slider } from ".";

const meta = {
  title: "UI/Slider",
  component: Slider,
  argTypes: {
    min: { control: "number" },
    max: { control: "number" },
    step: { control: "number" },
    disabled: { control: "boolean" },
  },
  args: { min: 0, max: 100, step: 1, disabled: false },
  render: (args) => ({
    components: { Slider },
    setup: () => ({ args, value: ref([40]) }),
    template: `
      <div class="w-[320px] space-y-3">
        <Slider v-bind="args" v-model="value" />
        <p class="text-muted-foreground text-sm">Waarde: {{ value.join(" – ") }}</p>
      </div>`,
  }),
} satisfies Meta<typeof Slider>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Disabled: Story = { args: { disabled: true } };

export const Range: Story = {
  render: (args) => ({
    components: { Slider },
    setup: () => ({ args, value: ref([20, 75]) }),
    template: `
      <div class="w-[320px] space-y-3">
        <Slider v-bind="args" v-model="value" />
        <p class="text-muted-foreground text-sm">Bereik: {{ value.join(" – ") }}</p>
      </div>`,
  }),
};
