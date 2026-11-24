import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ScrollArea, ScrollBar } from ".";

const meta = {
  title: "UI/ScrollArea",
  component: ScrollArea,
} satisfies Meta<typeof ScrollArea>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Vertical: Story = {
  render: () => ({
    components: { ScrollArea },
    setup: () => ({ items: Array.from({ length: 50 }, (_, i) => `Sensor ${i + 1}`) }),
    template: `
      <ScrollArea class="h-72 w-56 rounded-md border">
        <div class="p-4">
          <p v-for="item in items" :key="item" class="border-b py-2 text-sm">{{ item }}</p>
        </div>
      </ScrollArea>`,
  }),
};

export const Horizontal: Story = {
  render: () => ({
    components: { ScrollArea, ScrollBar },
    setup: () => ({ items: Array.from({ length: 20 }, (_, i) => i + 1) }),
    template: `
      <ScrollArea class="w-96 rounded-md border whitespace-nowrap">
        <div class="flex w-max gap-4 p-4">
          <div v-for="i in items" :key="i" class="bg-muted flex h-24 w-32 items-center justify-center rounded-md">
            Module {{ i }}
          </div>
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>`,
  }),
};
