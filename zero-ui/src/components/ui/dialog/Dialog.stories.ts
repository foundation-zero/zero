import type { Meta, StoryObj } from "@storybook/vue3-vite";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
  DialogTrigger,
} from ".";
import { Button } from "../button";
import { Input } from "../input";
import { Label } from "../label";

const components = {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogScrollContent,
  DialogTitle,
  DialogTrigger,
  Input,
  Label,
};

const meta = {
  title: "UI/Dialog",
  component: Dialog,
} satisfies Meta<typeof Dialog>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components,
    template: `
      <Dialog>
        <DialogTrigger as-child><Button>Open dialoog</Button></DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Setpoint aanpassen</DialogTitle>
            <DialogDescription>Wijzig de doeltemperatuur van de tank.</DialogDescription>
          </DialogHeader>
          <div class="grid gap-2">
            <Label for="setpoint">Temperatuur (°C)</Label>
            <Input id="setpoint" type="number" model-value="60" />
          </div>
          <DialogFooter>
            <DialogClose as-child><Button variant="secondary">Annuleren</Button></DialogClose>
            <DialogClose as-child><Button>Opslaan</Button></DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>`,
  }),
};

export const ScrollContent: Story = {
  render: () => ({
    components,
    setup: () => ({ items: Array.from({ length: 40 }, (_, i) => i + 1) }),
    template: `
      <Dialog>
        <DialogTrigger as-child><Button variant="secondary">Lange dialoog</Button></DialogTrigger>
        <DialogScrollContent>
          <DialogHeader>
            <DialogTitle>Logboek</DialogTitle>
            <DialogDescription>Een dialoog met veel inhoud die scrollt.</DialogDescription>
          </DialogHeader>
          <p v-for="i in items" :key="i" class="text-sm">Regel {{ i }}</p>
        </DialogScrollContent>
      </Dialog>`,
  }),
};
