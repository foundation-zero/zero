import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Popover, PopoverContent, PopoverTrigger } from ".";
import { Button } from "../button";
import { Input } from "../input";
import { Label } from "../label";

const meta = {
  title: "UI/Popover",
  component: Popover,
} satisfies Meta<typeof Popover>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components: { Button, Input, Label, Popover, PopoverContent, PopoverTrigger },
    template: `
      <Popover>
        <PopoverTrigger as-child><Button variant="secondary">Open popover</Button></PopoverTrigger>
        <PopoverContent class="w-72">
          <div class="grid gap-2">
            <p class="text-sm font-semibold">Afmetingen</p>
            <Label for="breedte">Breedte</Label>
            <Input id="breedte" model-value="100%" />
          </div>
        </PopoverContent>
      </Popover>`,
  }),
};
