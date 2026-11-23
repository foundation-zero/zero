import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { Switch } from ".";
import { Label } from "../label";

const meta = {
  title: "UI/Switch",
  component: Switch,
  argTypes: { disabled: { control: "boolean" } },
  args: { disabled: false },
  render: (args) => ({
    components: { Label, Switch },
    setup: () => ({ args, on: ref(true) }),
    template: `
      <div class="flex items-center gap-2">
        <Switch id="sw" v-bind="args" v-model="on" />
        <Label for="sw">Automatisch ({{ on ? "aan" : "uit" }})</Label>
      </div>`,
  }),
} satisfies Meta<typeof Switch>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Disabled: Story = { args: { disabled: true } };
