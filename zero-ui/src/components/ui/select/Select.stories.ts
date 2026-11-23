import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import {
  MultiSelectTrigger,
  MultiSelectValue,
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectTriggerLabel,
  SelectValue,
} from ".";

const components = {
  MultiSelectTrigger,
  MultiSelectValue,
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectTriggerLabel,
  SelectValue,
};

const modules = ["thrusters", "dhw", "pvt", "pcm", "consumers"];

const meta = {
  title: "UI/Select",
  component: Select,
} satisfies Meta<typeof Select>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components,
    setup: () => ({ modules, value: ref<string>() }),
    template: `
      <Select v-model="value">
        <SelectTrigger class="w-[240px]">
          <SelectValue placeholder="Kies een module" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="m in modules" :key="m" :value="m">{{ m }}</SelectItem>
        </SelectContent>
      </Select>`,
  }),
};

export const Small: Story = {
  render: () => ({
    components,
    setup: () => ({ modules }),
    template: `
      <Select>
        <SelectTrigger size="sm" class="w-[200px]">
          <SelectValue placeholder="Klein formaat" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="m in modules" :key="m" :value="m">{{ m }}</SelectItem>
        </SelectContent>
      </Select>`,
  }),
};

export const Groups: Story = {
  render: () => ({
    components,
    template: `
      <Select>
        <SelectTrigger class="w-[240px]">
          <SelectValue placeholder="Kies een systeem" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Thermisch</SelectLabel>
            <SelectItem value="dhw">DHW</SelectItem>
            <SelectItem value="pcm">PCM</SelectItem>
          </SelectGroup>
          <SelectSeparator />
          <SelectGroup>
            <SelectLabel>Voortstuwing</SelectLabel>
            <SelectItem value="thrusters">Thrusters</SelectItem>
            <SelectItem value="drives" disabled>Drives (binnenkort)</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>`,
  }),
};

export const WithTriggerLabel: Story = {
  render: () => ({
    components,
    setup: () => ({ modules, value: ref("dhw") }),
    template: `
      <Select v-model="value">
        <SelectTrigger class="relative h-12 w-[240px] pt-4">
          <SelectTriggerLabel>Module</SelectTriggerLabel>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem v-for="m in modules" :key="m" :value="m">{{ m }}</SelectItem>
        </SelectContent>
      </Select>`,
  }),
};

export const MultiSelect: Story = {
  render: () => ({
    components,
    setup: () => ({ modules, value: ref<string[]>(["dhw", "pvt"]) }),
    template: `
      <Select v-model="value" multiple>
        <MultiSelectTrigger class="w-[240px]">
          <MultiSelectValue>Modules</MultiSelectValue>
        </MultiSelectTrigger>
        <SelectContent>
          <SelectItem v-for="m in modules" :key="m" :value="m">{{ m }}</SelectItem>
        </SelectContent>
      </Select>`,
  }),
};
