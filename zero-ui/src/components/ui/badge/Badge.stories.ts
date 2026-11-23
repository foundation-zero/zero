import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Badge } from ".";

const variants = [
  "default",
  "secondary",
  "brand",
  "constructive",
  "warning",
  "destructive",
  "outline",
];

const meta = {
  title: "UI/Badge",
  component: Badge,
  argTypes: {
    variant: { control: "select", options: variants },
    type: { control: "select", options: ["default", "number"] },
  },
  args: { variant: "default", type: "default" },
  render: (args) => ({
    components: { Badge },
    setup: () => ({ args }),
    template: '<Badge v-bind="args">{{ args.type === "number" ? 3 : "Badge" }}</Badge>',
  }),
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Number: Story = { args: { type: "number", variant: "secondary" } };

export const AllVariants: Story = {
  render: () => ({
    components: { Badge },
    setup: () => ({ variants }),
    template: `
      <div class="flex flex-wrap gap-2">
        <Badge v-for="v in variants" :key="v" :variant="v">{{ v }}</Badge>
      </div>`,
  }),
};
