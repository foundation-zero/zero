import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Label } from ".";

const meta = {
  title: "UI/Label",
  component: Label,
  render: (args) => ({
    components: { Label },
    setup: () => ({ args }),
    template: '<Label v-bind="args">Doeltemperatuur</Label>',
  }),
} satisfies Meta<typeof Label>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
