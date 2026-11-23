import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { Input } from ".";
import { Label } from "../label";

const meta = {
  title: "UI/Input",
  component: Input,
  render: (args) => ({
    components: { Input },
    setup: () => ({ args, value: ref("") }),
    template: '<Input v-bind="args" v-model="value" placeholder="Typ iets…" class="w-[280px]" />',
  }),
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Disabled: Story = {
  render: () => ({
    components: { Input },
    template: '<Input disabled placeholder="Niet beschikbaar" class="w-[280px]" />',
  }),
};
export const Invalid: Story = {
  render: (args) => ({
    components: { Input },
    setup: () => ({ args }),
    template:
      '<Input v-bind="args" aria-invalid="true" model-value="ongeldig" class="w-[280px]" />',
  }),
};

export const WithLabel: Story = {
  render: () => ({
    components: { Input, Label },
    template: `
      <div class="grid w-[280px] gap-2">
        <Label for="naam">Naam</Label>
        <Input id="naam" placeholder="Bijv. Tank 2" />
      </div>`,
  }),
};
