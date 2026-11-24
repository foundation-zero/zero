import type { Meta, StoryObj } from "@storybook/vue3-vite";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from ".";
import { Button } from "../button";

const meta = {
  title: "UI/Drawer",
  component: Drawer,
} satisfies Meta<typeof Drawer>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components: {
      Button,
      Drawer,
      DrawerClose,
      DrawerContent,
      DrawerDescription,
      DrawerFooter,
      DrawerHeader,
      DrawerTitle,
      DrawerTrigger,
    },
    template: `
      <Drawer :should-scale-background="false">
        <DrawerTrigger as-child><Button>Open drawer</Button></DrawerTrigger>
        <DrawerContent>
          <div class="mx-auto w-full max-w-sm">
            <DrawerHeader>
              <DrawerTitle>Pompinstellingen</DrawerTitle>
              <DrawerDescription>Sleep omlaag of klik buiten de drawer om te sluiten.</DrawerDescription>
            </DrawerHeader>
            <DrawerFooter>
              <Button>Toepassen</Button>
              <DrawerClose as-child><Button variant="secondary">Annuleren</Button></DrawerClose>
            </DrawerFooter>
          </div>
        </DrawerContent>
      </Drawer>`,
  }),
};
