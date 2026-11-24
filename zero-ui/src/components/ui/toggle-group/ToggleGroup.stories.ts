import {
  RiAlignCenter,
  RiAlignLeft,
  RiAlignRight,
  RiBold,
  RiItalic,
  RiUnderline,
} from "@remixicon/vue";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { ToggleGroup, ToggleGroupItem } from ".";

const components = {
  RiAlignCenter,
  RiAlignLeft,
  RiAlignRight,
  RiBold,
  RiItalic,
  RiUnderline,
  ToggleGroup,
  ToggleGroupItem,
};

// ToggleGroup is een generiek component, dus de meta wordt hier zonder componenttype getypeerd.
const meta: Meta = {
  title: "UI/ToggleGroup",
};

export default meta;
type Story = StoryObj;

export const Single: Story = {
  render: () => ({
    components,
    setup: () => ({ value: ref("left") }),
    template: `
      <ToggleGroup type="single" v-model="value">
        <ToggleGroupItem value="left" aria-label="Links"><RiAlignLeft /></ToggleGroupItem>
        <ToggleGroupItem value="center" aria-label="Midden"><RiAlignCenter /></ToggleGroupItem>
        <ToggleGroupItem value="right" aria-label="Rechts"><RiAlignRight /></ToggleGroupItem>
      </ToggleGroup>`,
  }),
};

export const Multiple: Story = {
  render: () => ({
    components,
    setup: () => ({ value: ref(["bold"]) }),
    template: `
      <ToggleGroup type="multiple" variant="outline" v-model="value">
        <ToggleGroupItem value="bold" aria-label="Vet"><RiBold /></ToggleGroupItem>
        <ToggleGroupItem value="italic" aria-label="Cursief"><RiItalic /></ToggleGroupItem>
        <ToggleGroupItem value="underline" aria-label="Onderstreept"><RiUnderline /></ToggleGroupItem>
      </ToggleGroup>`,
  }),
};
