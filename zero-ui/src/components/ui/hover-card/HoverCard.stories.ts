import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { HoverCard, HoverCardContent, HoverCardTrigger } from ".";
import { Button } from "../button";

const meta = {
  title: "UI/HoverCard",
  component: HoverCard,
} satisfies Meta<typeof HoverCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components: { Button, HoverCard, HoverCardContent, HoverCardTrigger },
    template: `
      <HoverCard>
        <HoverCardTrigger as-child><Button variant="link">Thruster aft</Button></HoverCardTrigger>
        <HoverCardContent class="w-72">
          <p class="text-sm font-semibold">Thruster aft</p>
          <p class="text-muted-foreground text-sm">Koelwatertemperatuur 32,1 °C · pomp 1 actief</p>
        </HoverCardContent>
      </HoverCard>`,
  }),
};
