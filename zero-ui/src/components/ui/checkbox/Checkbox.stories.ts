import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { Checkbox } from ".";
import { Label } from "../label";

const meta = {
  title: "UI/Checkbox",
  component: Checkbox,
  argTypes: { disabled: { control: "boolean" } },
  args: { disabled: false },
  render: (args) => ({
    components: { Checkbox, Label },
    setup: () => ({ args, checked: ref<boolean | "indeterminate">(false) }),
    template: `
      <div class="flex items-center gap-2">
        <Checkbox id="cb" v-bind="args" v-model="checked" />
        <Label for="cb">Automatische modus</Label>
      </div>`,
  }),
} satisfies Meta<typeof Checkbox>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Disabled: Story = { args: { disabled: true } };

export const Indeterminate: Story = {
  render: () => ({
    components: { Checkbox, Label },
    setup: () => ({ checked: ref<boolean | "indeterminate">("indeterminate") }),
    template: `
      <div class="flex items-center gap-2">
        <Checkbox id="cb-i" v-model="checked" />
        <Label for="cb-i">Gedeeltelijk geselecteerd</Label>
      </div>`,
  }),
};
