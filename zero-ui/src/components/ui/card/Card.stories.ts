import { RiSettings3Line } from "@remixicon/vue";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from ".";
import { Button } from "../button";

const components = {
  Button,
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  RiSettings3Line,
};

const meta = {
  title: "UI/Card",
  component: Card,
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components,
    template: `
      <Card class="w-[360px]">
        <CardHeader>
          <CardTitle>Domestic hot water</CardTitle>
          <CardDescription>Tanktemperaturen en pompstatus</CardDescription>
          <CardAction>
            <Button size="icon" variant="ghost" aria-label="Instellingen"><RiSettings3Line /></Button>
          </CardAction>
        </CardHeader>
        <CardContent>
          <p class="text-sm">Tank 2: 58,4 °C · Tank 3: 61,0 °C</p>
        </CardContent>
        <CardFooter class="gap-2">
          <Button variant="secondary">Annuleren</Button>
          <Button>Opslaan</Button>
        </CardFooter>
      </Card>`,
  }),
};

export const ContentOnly: Story = {
  render: () => ({
    components,
    template: `
      <Card class="w-[360px]">
        <CardContent>Een kaart met alleen inhoud.</CardContent>
      </Card>`,
  }),
};
