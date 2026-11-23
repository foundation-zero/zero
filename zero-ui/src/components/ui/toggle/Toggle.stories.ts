import { RiBold } from "@remixicon/vue";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Toggle } from ".";

const meta = {
  title: "UI/Toggle",
  component: Toggle,
  argTypes: {
    variant: { control: "select", options: ["default", "outline"] },
    size: { control: "select", options: ["default", "sm", "lg"] },
    disabled: { control: "boolean" },
  },
  args: { variant: "default", size: "default", disabled: false },
  render: (args) => ({
    components: { RiBold, Toggle },
    setup: () => ({ args }),
    template: '<Toggle v-bind="args" aria-label="Vet"><RiBold /></Toggle>',
  }),
} satisfies Meta<typeof Toggle>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Outline: Story = { args: { variant: "outline" } };
export const WithText: Story = {
  render: (args) => ({
    components: { RiBold, Toggle },
    setup: () => ({ args }),
    template: '<Toggle v-bind="args"><RiBold />Vet</Toggle>',
  }),
};
