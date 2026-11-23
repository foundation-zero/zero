import { RiMailLine, RiSearchLine } from "@remixicon/vue";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
  InputGroupText,
  InputGroupTextarea,
} from ".";

const components = {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
  InputGroupText,
  InputGroupTextarea,
  RiMailLine,
  RiSearchLine,
};

const meta = {
  title: "UI/InputGroup",
  component: InputGroup,
} satisfies Meta<typeof InputGroup>;

export default meta;
type Story = StoryObj<typeof meta>;

export const WithIcon: Story = {
  render: () => ({
    components,
    template: `
      <InputGroup class="w-[320px]">
        <InputGroupInput placeholder="Zoeken…" />
        <InputGroupAddon><RiSearchLine /></InputGroupAddon>
      </InputGroup>`,
  }),
};

export const WithTextAndButton: Story = {
  render: () => ({
    components,
    template: `
      <InputGroup class="w-[320px]">
        <InputGroupInput placeholder="60" />
        <InputGroupAddon align="inline-end">
          <InputGroupText>°C</InputGroupText>
          <InputGroupButton variant="secondary">Zet</InputGroupButton>
        </InputGroupAddon>
      </InputGroup>`,
  }),
};

export const Textarea: Story = {
  render: () => ({
    components,
    template: `
      <InputGroup class="w-[360px]">
        <InputGroupTextarea placeholder="Notitie voor de bemanning…" />
        <InputGroupAddon align="block-end">
          <InputGroupText><RiMailLine /> Wordt gedeeld met het team</InputGroupText>
          <InputGroupButton class="ml-auto" size="sm" variant="default">Versturen</InputGroupButton>
        </InputGroupAddon>
      </InputGroup>`,
  }),
};
