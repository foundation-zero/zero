import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { TotalsTable } from ".";

const meta = {
  title: "THRS/Monitoring/TotalsTable",
  component: TotalsTable,
  parameters: { layout: "padded" },
  args: {
    title: "Heat delivered in range",
    assetHeader: "Source",
    valueHeader: "Energy",
    unit: "kWh",
    rows: [
      { asset: "HT boosting", value: 2.42, color: "#eda100" },
      { asset: "DC recovery", value: 1.14, color: "#eb6834" },
      { asset: "HVAC recovery", value: 0.32, color: "#e87ba4" },
      { asset: "Adsorption recovery", value: 0.05, color: "#2a78d6" },
      { asset: "Heat pump", value: 0, color: "#008300" },
    ],
  },
  render: (args) => ({
    components: { TotalsTable },
    setup: () => ({ args }),
    template: `<div class="h-[420px] w-[360px]"><TotalsTable v-bind="args" class="h-full" /></div>`,
  }),
} satisfies Meta<typeof TotalsTable>;

export default meta;
type Story = StoryObj<typeof meta>;

export const HeatDelivered: Story = {};

export const WaterUsed: Story = {
  args: {
    title: "Water used in range",
    assetHeader: "Line",
    valueHeader: "Volume",
    unit: "L",
    rows: [
      { asset: "Fill line via DC", value: 125.35, color: "#2a78d6" },
      { asset: "Fill line via drives", value: 0, color: "#eb6834" },
    ],
  },
};
