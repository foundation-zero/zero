import { RiAddLine, RiSettings3Line } from "@remixicon/vue";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Button } from ".";

const variants = ["default", "secondary", "ghost", "link", "outline"];

const meta = {
  title: "UI/Button",
  component: Button,
  argTypes: {
    variant: { control: "select", options: variants },
    size: { control: "select", options: ["default", "sm", "lg", "icon"] },
  },
  args: { variant: "default", size: "default" },
  render: (args) => ({
    components: { Button },
    setup: () => ({ args }),
    template: '<Button v-bind="args">Knop</Button>',
  }),
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Secondary: Story = { args: { variant: "secondary" } };
export const Ghost: Story = { args: { variant: "ghost" } };
export const Link: Story = { args: { variant: "link" } };
export const Outline: Story = { args: { variant: "outline" } };
export const Disabled: Story = {
  render: (args) => ({
    components: { Button },
    setup: () => ({ args }),
    template: '<Button v-bind="args" disabled>Knop</Button>',
  }),
};

export const WithIcon: Story = {
  render: (args) => ({
    components: { Button, RiAddLine },
    setup: () => ({ args }),
    template: '<Button v-bind="args"><RiAddLine />Toevoegen</Button>',
  }),
};

export const IconOnly: Story = {
  args: { size: "icon", variant: "secondary" },
  render: (args) => ({
    components: { Button, RiSettings3Line },
    setup: () => ({ args }),
    template: '<Button v-bind="args" aria-label="Instellingen"><RiSettings3Line /></Button>',
  }),
};

export const AllVariants: Story = {
  render: () => ({
    components: { Button },
    setup: () => ({ variants }),
    template: `
      <div class="flex flex-wrap items-center gap-3">
        <Button v-for="v in variants" :key="v" :variant="v">{{ v }}</Button>
      </div>`,
  }),
};
