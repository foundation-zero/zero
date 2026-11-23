import { RiInboxLine } from "@remixicon/vue";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from ".";
import { Button } from "../button";

const meta = {
  title: "UI/Empty",
  component: Empty,
} satisfies Meta<typeof Empty>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components: {
      Button,
      Empty,
      EmptyContent,
      EmptyDescription,
      EmptyHeader,
      EmptyMedia,
      EmptyTitle,
      RiInboxLine,
    },
    template: `
      <Empty class="w-[420px] border">
        <EmptyHeader>
          <EmptyMedia variant="icon"><RiInboxLine /></EmptyMedia>
          <EmptyTitle>Geen alarmen</EmptyTitle>
          <EmptyDescription>Er zijn op dit moment geen actieve alarmen.</EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button variant="secondary">Bekijk historie</Button>
        </EmptyContent>
      </Empty>`,
  }),
};
