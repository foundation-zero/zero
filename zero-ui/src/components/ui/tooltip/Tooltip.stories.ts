import { RiInformationLine } from "@remixicon/vue";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from ".";
import { Button } from "../button";

const components = {
  Button,
  RiInformationLine,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
};

const meta = {
  title: "UI/Tooltip",
  component: Tooltip,
} satisfies Meta<typeof Tooltip>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components,
    template: `
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger as-child>
            <Button size="icon" variant="ghost" aria-label="Info"><RiInformationLine /></Button>
          </TooltipTrigger>
          <TooltipContent>Laatst bijgewerkt: 5 seconden geleden</TooltipContent>
        </Tooltip>
      </TooltipProvider>`,
  }),
};

export const Sides: Story = {
  render: () => ({
    components,
    setup: () => ({ sides: ["top", "right", "bottom", "left"] }),
    template: `
      <TooltipProvider>
        <div class="flex gap-3">
          <Tooltip v-for="s in sides" :key="s">
            <TooltipTrigger as-child><Button variant="secondary">{{ s }}</Button></TooltipTrigger>
            <TooltipContent :side="s">Tooltip aan de {{ s }}-kant</TooltipContent>
          </Tooltip>
        </div>
      </TooltipProvider>`,
  }),
};
