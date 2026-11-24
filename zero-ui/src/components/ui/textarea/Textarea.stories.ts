import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { Textarea } from ".";

const meta = {
  title: "UI/Textarea",
  component: Textarea,
  render: (args) => ({
    components: { Textarea },
    setup: () => ({ args, value: ref("") }),
    template:
      '<Textarea v-bind="args" v-model="value" placeholder="Schrijf een notitie…" class="w-[360px]" />',
  }),
} satisfies Meta<typeof Textarea>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Disabled: Story = {
  render: () => ({
    components: { Textarea },
    template: '<Textarea disabled placeholder="Niet beschikbaar" class="w-[360px]" />',
  }),
};
