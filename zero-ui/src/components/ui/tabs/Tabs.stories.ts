import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { Tabs, TabsContent, TabsList, TabsTrigger } from ".";

const meta = {
  title: "UI/Tabs",
  component: Tabs,
} satisfies Meta<typeof Tabs>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components: { Tabs, TabsContent, TabsList, TabsTrigger },
    template: `
      <Tabs default-value="overzicht" class="w-[400px]">
        <TabsList>
          <TabsTrigger value="overzicht">Overzicht</TabsTrigger>
          <TabsTrigger value="parameters">Parameters</TabsTrigger>
          <TabsTrigger value="historie" disabled>Historie</TabsTrigger>
        </TabsList>
        <TabsContent value="overzicht" class="text-sm">Live waarden van de module.</TabsContent>
        <TabsContent value="parameters" class="text-sm">Instelbare parameters.</TabsContent>
      </Tabs>`,
  }),
};
