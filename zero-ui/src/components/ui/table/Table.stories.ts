import type { Meta, StoryObj } from "@storybook/vue3-vite";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableEmpty,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from ".";

const components = {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableEmpty,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
};

const rows = [
  { sensor: "Tank 2", value: "58,4", unit: "°C" },
  { sensor: "Tank 3", value: "61,0", unit: "°C" },
  { sensor: "HVAC return", value: "42,7", unit: "°C" },
  { sensor: "DC return", value: "39,9", unit: "°C" },
];

const meta = {
  title: "UI/Table",
  component: Table,
  parameters: { layout: "padded" },
} satisfies Meta<typeof Table>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => ({
    components,
    setup: () => ({ rows }),
    template: `
      <Table>
        <TableCaption>Temperatuursensoren DHW</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Sensor</TableHead>
            <TableHead class="text-right">Waarde</TableHead>
            <TableHead>Eenheid</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="r in rows" :key="r.sensor">
            <TableCell class="font-medium">{{ r.sensor }}</TableCell>
            <TableCell class="text-right">{{ r.value }}</TableCell>
            <TableCell>{{ r.unit }}</TableCell>
          </TableRow>
        </TableBody>
        <TableFooter>
          <TableRow>
            <TableCell>Gemiddeld</TableCell>
            <TableCell class="text-right">50,5</TableCell>
            <TableCell>°C</TableCell>
          </TableRow>
        </TableFooter>
      </Table>`,
  }),
};

export const Empty: Story = {
  render: () => ({
    components,
    template: `
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Sensor</TableHead>
            <TableHead>Waarde</TableHead>
            <TableHead>Eenheid</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableEmpty :colspan="3">Geen gegevens beschikbaar</TableEmpty>
        </TableBody>
      </Table>`,
  }),
};
