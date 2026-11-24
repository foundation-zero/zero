import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { HeatDistribution } from ".";

const meta = {
  title: "THRS/Monitoring/HeatDistribution",
  component: HeatDistribution,
  parameters: { layout: "padded" },
  args: {
    unit: "kWh",
    rows: [
      { asset: "HT boosting", value: 3.68, color: "#eda100" },
      { asset: "DC recovery", value: 1.95, color: "#eb6834" },
      { asset: "HVAC recovery", value: 0.7, color: "#e87ba4" },
      { asset: "Adsorption recovery", value: 0.06, color: "#2a78d6" },
      { asset: "Heat pump", value: 0, color: "#008300" },
    ],
  },
  render: (args) => ({
    components: { HeatDistribution },
    setup: () => ({ args }),
    template: `<div class="max-w-[1500px]"><HeatDistribution v-bind="args" /></div>`,
  }),
} satisfies Meta<typeof HeatDistribution>;

export default meta;
type Story = StoryObj<typeof meta>;

/** Sources that delivered nothing get no tile and no slice. */
export const SixHours: Story = {};
export const NoHeat: Story = { args: { rows: [] } };
export const Failed: Story = { args: { rows: [], error: "GreptimeDB timed out" } };
